"""GitHub-only production/review state. Never calls a TikTok publishing endpoint."""
from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo
from pathlib import Path
import hashlib, json, os, re, subprocess, sys

REPO='estebansanchezoficial/reto-visual-70'
OWNER='estebansanchezoficial'
PREFIX='rv70-review-'
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'output/current'
NOW=lambda:datetime.now(ZoneInfo('America/Mexico_City'))

def gh(*args, payload=None):
    p=subprocess.run(['gh',*args],input=json.dumps(payload) if payload is not None else None,text=True,capture_output=True)
    if p.returncode:raise RuntimeError(f'GitHub operation failed ({args[0]}): {p.stderr[:500]}')
    return p.stdout

def api(path,payload=None):
    args=['api',path]
    if payload is not None:args+=['--method','POST','--input','-']
    return json.loads(gh(*args,payload=payload))

def releases():
    return [r for page in json.loads(gh('api',f'repos/{REPO}/releases?per_page=100','--paginate','--slurp')) for r in page if r['tag_name'].startswith(PREFIX)]

def state(release):
    return json.loads(release['body'])

def issues():
    return json.loads(gh('issue','list','-R',REPO,'--state','all','--limit','500','--json','number,body,state,title'))

def issue_for(tag):
    return next((i for i in issues() if f'<!-- {tag} -->' in i['body']),None)

def target_date():
    return max(NOW().date()+timedelta(days=1),date(2026,11,1)).isoformat()

def prepare():
    repo=api(f'repos/{REPO}')
    assert repo['private'] is False, 'Stop: free public-runner condition changed'
    current=releases()
    # Keep one package until scheduling is explicitly reported. No backlog/retries.
    if any(state(r)['status']!='SCHEDULED_USER_REPORTED' for r in current):
        print('Existing unresolved package: no generation or retry.');return
    day=target_date();tag=PREFIX+day+'-v1'
    if any(r['tag_name']==tag for r in current):print('Date already reserved.');return
    record={'status':'PREPARING','date':day,'scheduled':False,'published':False}
    gh('release','create',tag,'-R',REPO,'--draft','--target','main','--title',f'Reto Visual 70 — revisión {day}','--notes',json.dumps(record))
    try:
        subprocess.run([sys.executable,str(ROOT/'daily/prepare_models.py')],check=True)
        subprocess.run([sys.executable,str(ROOT/'daily/generate.py'),'--date',day],check=True)
        qa=json.loads((OUT/'verificacion-final.json').read_text())
        assert qa['status']=='PASS_PENDING_USER_APPROVAL'
        names=['video.mp4','portada.jpg','descripcion.txt','verificacion-final.json','manifest.json','plan.json','revision.jpg','narracion.json']
        gh('release','upload',tag,*[str(OUT/n) for n in names],'-R',REPO)
        # Verify remote bytes, not only upload exit status.
        verify=ROOT/'output/download-check';verify.mkdir(exist_ok=True,parents=True)
        gh('release','download',tag,'-R',REPO,'--pattern','video.mp4','--dir',str(verify))
        assert hashlib.sha256((verify/'video.mp4').read_bytes()).hexdigest()==qa['sha256']
        record.update(status='READY_FOR_REVIEW',sha256=qa['sha256'],bytes=qa['bytes'],run_url=os.environ.get('RUN_URL'))
        gh('release','edit',tag,'-R',REPO,'--notes',json.dumps(record))
        print(json.dumps(record))
    except Exception:
        record['status']='FAILED_NEEDS_REVIEW'
        gh('release','edit',tag,'-R',REPO,'--notes',json.dumps(record))
        raise

def notify():
    for release in releases():
        record=state(release);tag=release['tag_name']
        if record['status']=='SCHEDULED_USER_REPORTED' or issue_for(tag):continue
        url=release['html_url']
        if record['status']=='READY_FOR_REVIEW':
            sha=record['sha256']
            body=f'''<!-- {tag} -->
Video listo para revisar desde el teléfono. Abre la entrega con tu sesión de GitHub e inicia **video.mp4**; contiene la voz Alex. Descarga también portada.jpg y descripcion.txt si vas a publicarlo.

**[Abrir entrega y video]({url})** · Fecha propuesta: **{record['date']} a las 19:00, Ciudad de México**.

70 s · 1080 × 1920 · 30 FPS · avatar abrazando el acertijo · prueba técnica y descarga verificadas.

Para aprobar este archivo exacto, comenta esta línea (puedes copiarla desde el teléfono):

`APROBAR {sha}`

Para pedir cambios: `CORREGIR: explica el cambio`.

La aprobación registra tu decisión; **no significa que esté programado en TikTok**. La música nativa se añade en TikTok: Inside Algorithm — Cool Ember Sync, suave (-24 dB), entrada 1 s y salida 2 s. Mantener activado «Creado por IA». La disponibilidad de la canción debe comprobarse allí.

Después de programarlo realmente, registra el enlace de TikTok con:

`REGISTRAR_PROGRAMADO {sha} https://www.tiktok.com/@retovisual70/video/ID`

El sistema bloqueará otro video mientras esta entrega siga pendiente. Si la fecha ya pasó, hay que escoger otra fecha antes de programar. No se publica automáticamente.

SHA-256: `{sha}`
Ejecución: {record.get('run_url','')}
'''
            title=f"Revisar video — {record['date']} · Reto Visual 70"
        else:
            title=f"Atención: preparación {record['date']} · Reto Visual 70"
            body=f"<!-- {tag} -->\nEstado: {record['status']}. No se generará otro video ni se reintentará automáticamente. Revisa [Actions](https://github.com/{REPO}/actions) antes de intervenir."
        result=api(f'repos/{REPO}/issues',{'title':title,'body':body,'assignees':[OWNER]})
        print('Review notification:',result['html_url'])

def comment():
    event=json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text())
    if event['sender']['login']!=OWNER or event['comment']['user']['login']!=OWNER:return
    if event['issue'].get('pull_request'):return
    match=re.search(r'<!-- (rv70-review-\d{4}-\d{2}-\d{2}-v1) -->',event['issue']['body'] or '')
    if not match:return
    tag=match.group(1);release=next(r for r in releases() if r['tag_name']==tag);record=state(release)
    text=event['comment']['body'].strip();sha=record.get('sha256')
    if text==f'APROBAR {sha}' and sha and record['status']=='READY_FOR_REVIEW':
        folder=ROOT/'output/approval-check';folder.mkdir(parents=True,exist_ok=True)
        gh('release','download',tag,'-R',REPO,'--pattern','video.mp4','--dir',str(folder))
        assert hashlib.sha256((folder/'video.mp4').read_bytes()).hexdigest()==sha
        record.update(status='APPROVED_PENDING_TIKTOK',approval_comment=event['comment']['html_url'])
        message='Aprobación registrada para este SHA-256. **Pendiente programar realmente en TikTok** con aviso de IA y música nativa. Esta acción no publica ni programa el video.'
    elif text.startswith('CORREGIR:') and record['status'] in ['READY_FOR_REVIEW','APPROVED_PENDING_TIKTOK']:
        record['status']='CORRECTION_REQUESTED';message='Cambio registrado. Se bloquea la generación siguiente hasta resolver y revisar una nueva versión; esta aprobación no se reutilizará.'
    elif sha and re.fullmatch(rf'REGISTRAR_PROGRAMADO {sha} https://www\.tiktok\.com/@retovisual70/video/\d+',text) and record['status']=='APPROVED_PENDING_TIKTOK':
        record.update(status='SCHEDULED_USER_REPORTED',tiktok_url=text.split()[-1],scheduled=True,published=False)
        message='Programación declarada por el propietario y enlace guardado. No se ha verificado su estado directamente en TikTok. Se habilita la preparación siguiente.'
    else:return
    gh('release','edit',tag,'-R',REPO,'--notes',json.dumps(record))
    api(f"repos/{REPO}/issues/{event['issue']['number']}/comments",{'body':message})
    if record['status']=='SCHEDULED_USER_REPORTED':
        gh('issue','close',str(event['issue']['number']),'-R',REPO)

if __name__=='__main__':
    assert os.environ.get('GITHUB_REPOSITORY',REPO)==REPO
    {'prepare':prepare,'notify':notify,'comment':comment}[sys.argv[1]]()
