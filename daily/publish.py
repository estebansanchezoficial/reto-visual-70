"""Approval-bound cloud delivery. One creation attempt; ambiguous results stop."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo
import hashlib, json, os, re, subprocess, sys, urllib.request
import cloud
import buffer_api as buffer

PREFIX='rv70-publish-'
ACTIVE={'BUFFER_RESERVED','BUFFER_NEEDS_RECONCILIATION','SCHEDULED_VERIFIED_BUFFER'}


def validate(record, now=None):
    if record.get('status')!='APPROVED_PENDING_TIKTOK':
        raise ValueError('Exact version has not been approved or was already handled')
    sha=record.get('sha256','')
    if not re.fullmatch('[0-9a-f]{64}',sha) or not record.get('music_embedded'):
        raise ValueError('Only final, licensed music mixes can be sent')
    if not record.get('approval_comment') or record.get('scheduled') or record.get('published'):
        raise ValueError('Missing approval or delivery already exists')
    due=datetime.fromisoformat(record['date']+'T19:00:00').replace(tzinfo=ZoneInfo('America/Mexico_City'))
    if due < (now or datetime.now(timezone.utc))+timedelta(minutes=15):
        raise ValueError('Less than 15 minutes before target; choose a new date explicitly')
    return due.astimezone(timezone.utc).isoformat().replace('+00:00','Z')


def payload(caption, url, due, draft=False):
    parsed=urlsplit(url)
    if parsed.scheme!='https' or parsed.netloc!='github.com' or not parsed.path.startswith('/'+cloud.REPO+'/releases/download/'+PREFIX):
        raise ValueError('Media must be an immutable approved delivery in this repository')
    if 'Cipher' not in caption or 'Kevin MacLeod' not in caption or 'creativecommons.org/licenses/by/4.0/' not in caption:
        raise ValueError('Music credit missing')
    if len(caption)>2200:
        raise ValueError('Caption too long')
    result={'text':caption,'channelId':buffer.CHANNEL_ID,'schedulingType':'automatic',
            'mode':'addToQueue' if draft else 'customScheduled','saveToDraft':draft,'needsApproval':False,
            'assets':[{'video':{'url':url,'metadata':{'thumbnailOffset':8000}}}],
            'metadata':{'tiktok':{'isAiGenerated':True}}}
    if not draft:result['dueAt']=due
    return result


def verify_post(post, expected, draft=False):
    if post['channelId']!=buffer.CHANNEL_ID or post['text']!=expected['text'] or post['schedulingType']!='automatic':
        raise ValueError('Buffer destination/content/mode mismatch')
    if post.get('metadata',{}).get('isAiGenerated') is not True:
        raise ValueError('AI label was not retained')
    if draft:
        if post['status']!='draft':raise ValueError('Technical test must remain a draft')
    else:
        if post['status']!='scheduled' or datetime.fromisoformat(post['dueAt'].replace('Z','+00:00'))!=datetime.fromisoformat(expected['dueAt'].replace('Z','+00:00')):
            raise ValueError('Buffer did not retain the exact scheduled date/time')
    return post


def save(tag,record):
    cloud.gh('release','edit',tag,'-R',cloud.REPO,'--notes',json.dumps(record))


def notice(record,text):
    issue=record.get('review_issue')
    if issue:cloud.api(f'repos/{cloud.REPO}/issues/{issue}/comments',{'body':text})


def send(tag):
    if os.environ.get('RV70_BUFFER_ENABLED')!='true':raise ValueError('Cloud delivery not enabled')
    if not re.fullmatch(r'rv70-review-\d{4}-\d{2}-\d{2}-v\d+',tag):raise ValueError('Invalid review tag')
    if cloud.api(f'repos/{cloud.REPO}')['private']:raise ValueError('Public-runner condition changed')
    release=next(r for r in cloud.releases() if r['tag_name']==tag)
    record=cloud.state(release)
    due=validate(record)
    approval_id=record['approval_comment'].rsplit('-',1)[-1]
    if not approval_id.isdigit():raise ValueError('Invalid approval reference')
    approval=cloud.api(f'repos/{cloud.REPO}/issues/comments/{approval_id}')
    if approval['user']['login']!=cloud.OWNER or approval['body'].strip()!='APROBAR '+record['sha256']:
        raise ValueError('Approval no longer matches owner and final hash')
    connection=buffer.preflight()
    folder=cloud.ROOT/'output/buffer-delivery';folder.mkdir(parents=True)
    for name in ['video.mp4','descripcion.txt','verificacion-final.json']:
        cloud.gh('release','download',tag,'-R',cloud.REPO,'--pattern',name,'--dir',str(folder))
    video=folder/'video.mp4';sha=hashlib.sha256(video.read_bytes()).hexdigest()
    qa=json.loads((folder/'verificacion-final.json').read_text(encoding='utf-8'))
    if sha!=record['sha256'] or qa['sha256']!=sha or not qa.get('music_embedded'):
        raise ValueError('Downloaded package does not match exact approved video')
    issue=cloud.issue_for(tag)
    record.update(review_issue=issue['number'],status='BUFFER_RESERVED',buffer_due_at=due,buffer_channel_id=buffer.CHANNEL_ID,buffer_organization_id=connection['organization_id'])
    save(tag,record)  # Reserve before making public media or submitting a mutation.
    try:
        delivery=PREFIX+sha
        listing=cloud.api(f'repos/{cloud.REPO}/releases?per_page=100')
        if any(r['tag_name']==delivery for r in listing):raise ValueError('Delivery exists; reconcile instead of retrying')
        cloud.gh('release','create',delivery,'-R',cloud.REPO,'--draft','--target','main','--title',f"Approved TikTok delivery {record['date']}",'--notes',f"Approved SHA-256: {sha}. Music credit is included in descripcion.txt.")
        cloud.gh('release','upload',delivery,str(video),str(folder/'descripcion.txt'),'-R',cloud.REPO)
        cloud.gh('release','edit',delivery,'-R',cloud.REPO,'--draft=false','--latest=false')
        url=f'https://github.com/{cloud.REPO}/releases/download/{delivery}/video.mp4'
        with urllib.request.urlopen(url,timeout=40) as response:
            remote=response.read(20_000_001)
        if hashlib.sha256(remote).hexdigest()!=sha:raise ValueError('Public approved delivery hash mismatch')
        request=payload((folder/'descripcion.txt').read_text(encoding='utf-8').strip(),url,due)
        record.update(public_approved_media_url=url,buffer_request_sha256=hashlib.sha256(json.dumps(request,sort_keys=True).encode()).hexdigest())
        save(tag,record)
        created=buffer.create_post(request)
        record['buffer_post_id']=created['id']
        save(tag,record)  # Keep ID even if the following verification fails.
        post=verify_post(buffer.read_post(created['id']),request)
        record.update(status='SCHEDULED_VERIFIED_BUFFER',scheduled=True,published=False,buffer_status=post['status'],ai_label_enabled=True)
        save(tag,record)
        updated=cloud.api(f"repos/{cloud.REPO}/releases/{release['id']}")
        cloud.refresh_review_links(record['review_issue'],release,updated)
        cloud.review_page(updated)
        notice(record,f"Programación comprobada en Buffer para **{record['date']}, 19:00 Ciudad de México**, @retovisual70. Música integrada, crédito y aviso IA verificados. SHA `{sha}`. Buffer ID `{post['id']}`. Aún no está publicado en TikTok; se comprobará después de la hora prevista.")
        cloud.gh('issue','close',str(record['review_issue']),'-R',cloud.REPO)
    except Exception:
        record['status']='BUFFER_NEEDS_RECONCILIATION'
        save(tag,record)
        notice(record,'La programación necesita revisión. No se reintentará automáticamente para evitar duplicados. Comprobar Buffer y TikTok antes de intervenir. Ejecución: '+os.environ.get('RUN_URL',''))
        raise


if __name__=='__main__':
    send(os.environ['REVIEW_TAG'])
