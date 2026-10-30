"""GitHub-only production/review state. Never calls a TikTok publishing endpoint."""
from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo
from pathlib import Path
import hashlib, json, os, re, subprocess, sys
from urllib.parse import quote, urlsplit

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

def gate():
    current=releases();tag=PREFIX+target_date()+'-v1'
    allowed=not any(state(r)['status']!='SCHEDULED_USER_REPORTED' or r['tag_name']==tag for r in current)
    with Path(os.environ['GITHUB_OUTPUT']).open('a') as output:output.write(f'allowed={str(allowed).lower()}\n')
    print('New generation allowed:',allowed)

def prepare(repair=False):
    repo=api(f'repos/{REPO}')
    assert repo['private'] is False, 'Stop: free public-runner condition changed'
    current=releases()
    day=target_date();tag=PREFIX+day+'-v1'
    record={'status':'PREPARING','date':day,'scheduled':False,'published':False}
    if repair:
        reserved=next((r for r in current if r['tag_name']==tag),None)
        assert reserved and state(reserved)['status']=='FAILED_NEEDS_REVIEW' and not reserved['assets'], 'Repair requires a reviewed failed reservation with no uploaded assets'
        assert all(r['tag_name']==tag or state(r)['status']=='SCHEDULED_USER_REPORTED' for r in current)
        record['manual_repair_run']=os.environ.get('RUN_URL')
        gh('release','edit',tag,'-R',REPO,'--notes',json.dumps(record))
    else:
        # Keep one package until scheduling is explicitly reported. No backlog/retries.
        if any(state(r)['status']!='SCHEDULED_USER_REPORTED' for r in current):
            print('Existing unresolved package: no generation or retry.');return
        if any(r['tag_name']==tag for r in current):print('Date already reserved.');return
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
        if record['status']=='SCHEDULED_USER_REPORTED':continue
        existing=issue_for(tag)
        refresh=existing and record['status']=='READY_FOR_REVIEW' and record['sha256'] not in existing['body']
        marker=f'<!-- notice-{NOW().date().isoformat()} -->'
        if existing and not refresh:
            if record['status'] not in ['READY_FOR_REVIEW','APPROVED_PENDING_TIKTOK']:continue
            comments=api(f"repos/{REPO}/issues/{existing['number']}/comments?per_page=100")
            if marker in existing['body'] or any(marker in c['body'] for c in comments):continue
            api(f"repos/{REPO}/issues/{existing['number']}/comments",{'body':f"{marker}\nRevisión diaria 09:00: esta entrega sigue en {record['status']}. [Abrir video]({release['html_url']}). Fecha propuesta: {record['date']}, 19:00 Ciudad de México. Si ya venció, hace falta otra fecha antes de programar. No se ha creado otro video ni se ha publicado."})
            continue
        url=release['html_url']
        login_url='https://github.com/login?return_to='+quote(urlsplit(url).path,safe='')
        video_url=next((a['browser_download_url'] for a in release['assets'] if a['name']=='video.mp4'),url)
        if record['status']=='READY_FOR_REVIEW':
            sha=record['sha256']
            body=f'''<!-- {tag} -->
{marker}
Video listo para revisar desde el teléfono. La entrega está en borrador: abre el enlace en Chrome o Safari e inicia sesión como **estebansanchezoficial en ese navegador**. La sesión de GitHub Mobile no garantiza la sesión del navegador. Si «Entregas» aparece vacío o muestra 404, comprueba primero esa cuenta; los archivos no se han borrado.

**[Iniciar sesión y abrir la entrega]({login_url})** · **[Abrir o descargar video.mp4 con voz]({video_url})**

Dentro de la entrega abre **Assets / Recursos** si aparece plegado. Descarga también portada.jpg y descripcion.txt si vas a publicarlo.

**[Abrir entrega y video]({url})** · Fecha propuesta: **{record['date']} a las 19:00, Ciudad de México**.

Si GitHub cambia el enlace del borrador tras actualizar su estado, [abre Entregas](https://github.com/{REPO}/releases) y elige «Revisión {record['date']}».

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
        if refresh:
            gh('issue','edit',str(existing['number']),'-R',REPO,'--title',title,'--body',body)
            api(f"repos/{REPO}/issues/{existing['number']}/comments",{'body':f"Preparación corregida y verificada. [Abre la entrega y revisa video.mp4]({url}). El mensaje principal ya incluye la orden de aprobación con el hash exacto. No está programado ni publicado."})
            print('Review notification updated:',existing['number'])
        else:
            result=api(f'repos/{REPO}/issues',{'title':title,'body':body,'assignees':[OWNER]})
            print('Review notification:',result['html_url'])

def failure_notice():
    # Also covers dependency/download failures before a release reservation exists.
    notify()
    if any(state(r)['status']=='FAILED_NEEDS_REVIEW' for r in releases()):return
    marker=f'<!-- rv70-cloud-failure-{NOW().date().isoformat()} -->'
    if any(marker in i['body'] for i in issues()):return
    url=os.environ.get('RUN_URL',f'https://github.com/{REPO}/actions')
    api(f'repos/{REPO}/issues',{'title':'Atención: fallo de producción en nube · Reto Visual 70','body':f'{marker}\nLa ejecución no terminó correctamente. [Revisar el fallo]({url}). No se reintentará automáticamente ni se programó un video. Reconciliar cualquier entrega existente antes de intervenir.','assignees':[OWNER]})

def remind():
    for release in releases():
        record=state(release)
        if record['status']!='APPROVED_PENDING_TIKTOK' or record['date']!=NOW().date().isoformat():continue
        issue=issue_for(release['tag_name'])
        if not issue:continue
        marker=f"<!-- publish-reminder-{record['date']} -->"
        comments=api(f"repos/{REPO}/issues/{issue['number']}/comments?per_page=100")
        if any(marker in c['body'] for c in comments):continue
        api(f"repos/{REPO}/issues/{issue['number']}/comments",{'body':f"{marker}\nAviso previo a las 19:00: este archivo está aprobado, pero falta completar la publicación/programación en TikTok desde tu teléfono, con la música nativa y el aviso de IA activado. [Abrir entrega]({release['html_url']}). Verifica primero que no esté ya programado; no duplicar la carga. Si ya lo programaste, registra aquí el enlace con la orden indicada arriba."})

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
    {'prepare':prepare,'gate':gate,'repair':lambda:prepare(repair=True),'notify':notify,'comment':comment,'failure':failure_notice,'remind':remind}[sys.argv[1]]()
