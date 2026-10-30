"""Original, deterministic memory challenge. Local rendering only; no publishing API."""
from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import subprocess
import threading
import time

import PIL
from PIL import Image, ImageDraw, ImageFont
import psutil

ROOT = Path(__file__).resolve().parents[1]
W, H, FPS = 1080, 1920, 30
BG, PANEL, WHITE, MUTED = '#111022', '#211e38', '#f8f6ff', '#b5b0cd'
LIME, PURPLE = '#dcff78', '#b89cff'
NAMES = {'lemon':'LIMÓN', 'mug':'TAZA', 'key':'LLAVE', 'star':'ESTRELLA',
         'leaf':'HOJA', 'camera':'CÁMARA', 'heart':'CORAZÓN', 'umbrella':'PARAGUAS',
         'glasses':'LENTES', 'clock':'RELOJ', 'gift':'REGALO', 'moon':'LUNA'}
ROUNDS = [
    {'start':3, 'end':22, 'memory':6, 'search':8, 'objects':['lemon','mug','key','star'], 'missing':'key'},
    {'start':22, 'end':43, 'memory':7, 'search':9, 'objects':['leaf','camera','heart','umbrella','glasses','clock'], 'missing':'umbrella'},
    {'start':43, 'end':65, 'memory':8, 'search':9, 'objects':['gift','moon','lemon','mug','key','star','leaf','camera'], 'missing':'moon'},
]

@lru_cache(maxsize=40)
def font(size, bold=False):
    return ImageFont.truetype(str(ROOT/'assets/fonts'/('Barlow-Bold.ttf' if bold else 'Barlow-Regular.ttf')), size)

def text(d, xy, value, size=42, color=WHITE, bold=False, anchor=None):
    d.text(xy, value, font=font(size,bold), fill=color, anchor=anchor)

@lru_cache(maxsize=32)
def icon(name):
    im=Image.new('RGBA',(360,360)); d=ImageDraw.Draw(im)
    def line(points, fill=WHITE, width=16): d.line(points,fill=fill,width=width,joint='curve')
    if name=='lemon':
        d.ellipse((60,103,300,267),fill='#ffd665'); d.polygon([(60,170),(35,180),(65,199)],fill='#ffd665'); d.polygon([(290,170),(325,180),(294,200)],fill='#ffd665')
        d.arc((85,125,255,242),190,270,fill='#fff2b9',width=12)
    elif name=='mug':
        d.rounded_rectangle((236,125,316,234),radius=35,outline='#ffb4c8',width=24)
        d.rounded_rectangle((70,100,255,278),radius=30,fill='#ffb4c8'); d.ellipse((70,80,255,125),fill='#f9dce3'); d.ellipse((87,88,238,114),fill='#7d4361')
        line([(110,58),(118,35)],PURPLE,10); line([(165,55),(173,30)],PURPLE,10)
    elif name=='key':
        d.ellipse((48,61,187,200),outline='#ffcc72',width=29); line([(159,174),(286,301)],'#ffcc72',30)
        line([(220,231),(252,202)],'#ffcc72',26); line([(251,266),(283,237)],'#ffcc72',26)
    elif name=='star':
        pts=[(180+133*math.cos(-math.pi/2+i*math.pi/5)*(1 if i%2==0 else .46),180+133*math.sin(-math.pi/2+i*math.pi/5)*(1 if i%2==0 else .46)) for i in range(10)]
        d.polygon(pts,fill='#c4a4ff')
    elif name=='leaf':
        d.ellipse((72,38,288,297),fill='#83dfb0'); line([(110,284),(239,91)],'#287c69',14)
        line([(169,195),(119,149)],'#287c69',10); line([(192,163),(253,151)],'#287c69',10)
    elif name=='camera':
        d.rounded_rectangle((42,103,318,281),radius=30,fill='#8dd9ee'); d.rounded_rectangle((102,72,201,127),radius=16,fill='#8dd9ee')
        d.ellipse((111,123,250,262),fill='#23485d'); d.ellipse((139,151,222,234),fill='#b8f0fc'); d.ellipse((273,127,292,146),fill=WHITE)
    elif name=='heart':
        d.ellipse((48,72,191,218),fill='#ff829e'); d.ellipse((169,72,312,218),fill='#ff829e'); d.polygon([(51,166),(180,303),(309,166)],fill='#ff829e')
    elif name=='umbrella':
        d.pieslice((42,51,318,301),180,360,fill='#9ab5ff'); line([(180,171),(180,269)],'#dfe7ff',15)
        d.arc((112,236,182,304),0,180,fill='#dfe7ff',width=15); line([(42,177),(318,177)],'#dfe7ff',8)
    elif name=='glasses':
        d.rounded_rectangle((30,123,158,238),radius=39,outline='#ffc77d',width=18); d.rounded_rectangle((202,123,330,238),radius=39,outline='#ffc77d',width=18)
        d.arc((146,135,214,190),180,360,fill='#ffc77d',width=15); line([(20,142),(46,100)],'#ffc77d',15); line([(314,100),(340,142)],'#ffc77d',15)
    elif name=='clock':
        d.ellipse((55,55,305,305),fill='#9fe5d6'); d.ellipse((77,77,283,283),fill='#244a52'); line([(180,107),(180,182),(233,210)],'#d5fff1',14)
        for a in range(0,360,90):
            x,y=180+85*math.cos(math.radians(a)),180+85*math.sin(math.radians(a)); d.ellipse((x-6,y-6,x+6,y+6),fill=WHITE)
    elif name=='gift':
        d.rounded_rectangle((69,130,291,298),radius=15,fill='#ffbc9b'); d.rectangle((55,110,305,157),fill='#ffd3bb'); d.rectangle((163,110,197,299),fill='#b18aff')
        d.ellipse((101,58,180,119),outline='#c7a5ff',width=17); d.ellipse((180,58,259,119),outline='#c7a5ff',width=17)
    elif name=='moon':
        d.ellipse((56,42,306,310),fill='#ffe5a0'); d.ellipse((151,20,340,243),fill=PANEL)
    else: raise ValueError(name)
    return im.resize((164,164),Image.Resampling.LANCZOS)

def state(t):
    if t<3: return (-1,'intro',t,3)
    for i,r in enumerate(ROUNDS):
        if r['start']<=t<r['end']:
            local=t-r['start']; m=r['memory']; s=r['search']
            if local<m: return i,'memory',local,m
            if local<m+1: return i,'mask',local-m,1
            if local<m+1+s: return i,'search',local-m-1,s
            return i,'answer',local-m-1-s,4
    return 3,'outro',t-65,5

def survivors(r):
    items=[x for x in r['objects'] if x!=r['missing']]
    return list(reversed(items[1:]+items[:1]))

def validate_logic():
    assert [len(r['objects']) for r in ROUNDS]==[4,6,8]
    assert ROUNDS[0]['start']==3 and ROUNDS[-1]['end']==65
    for r in ROUNDS:
        assert len(set(r['objects']))==len(r['objects'])
        assert set(r['objects'])-set(survivors(r))=={r['missing']}
        assert len(survivors(r))==len(r['objects'])-1
        assert r['end']-r['start']==r['memory']+1+r['search']+4
        assert state(r['start']+r['memory']+.5)[1]=='mask'
        assert state(r['end']-.01)[1]=='answer'
    assert ROUNDS[0]['end']==ROUNDS[1]['start'] and ROUNDS[1]['end']==ROUNDS[2]['start']

def background():
    im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im)
    for y in range(H):
        p=y/H; d.line((0,y,W,y),fill=(int(17+8*p),int(16+5*p),int(34+14*p)))
    for x,y,r in [(960,370,360),(-120,1420,400)]:
        d.ellipse((x-r,y-r,x+r,y+r),outline='#29233f',width=2)
    return im

@lru_cache(maxsize=16)
def base(i,phase):
    im=background(); d=ImageDraw.Draw(im)
    text(d,(90,166),'RETO VISUAL',32,MUTED,True); text(d,(825,150),'70',57,LIME,True,anchor='ra')
    d.line((90,232,880,232),fill='#403850',width=2)
    text(d,(90,1610),'@retovisual70',33,MUTED)
    if phase in ('intro','outro'):
        text(d,(90,305),'MEMORIA / 001' if phase=='intro' else 'RETO COMPLETADO',31,LIME,True)
        lines=['¿QUÉ OBJETO','DESAPARECIÓ?'] if phase=='intro' else ['¿CUÁNTAS','ACERTASTE?']
        for j,line in enumerate(lines): text(d,(86,385+j*107),line,88,WHITE,True)
        text(d,(90,665),'3 rondas · de fácil a difícil' if phase=='intro' else 'Tu puntuación: 0, 1, 2 o 3',39,MUTED)
        for j,n in enumerate(['mug','star','camera'] if phase=='intro' else ['key','umbrella','moon']):
            im.paste(icon(n),(126+j*246,865),icon(n))
        text(d,(90,1160),'Mira. Recuerda. Encuentra.' if phase=='intro' else 'Escribe tu resultado',46,LIME,True)
        text(d,(90,1230),'Cada ronda tiene su respuesta.' if phase=='intro' else 'y sigue el próximo reto.',37,MUTED)
        d.rounded_rectangle((90,1385,875,1500),radius=26,fill=PANEL)
        text(d,(482,1442),'SIN PAUSAR' if phase=='intro' else '¿LOGRASTE 3 DE 3?',37,WHITE,True,anchor='mm')
        return im
    r=ROUNDS[i]
    text(d,(90,297),f'RONDA 0{i+1}',34,LIME,True)
    text(d,(90,353),['FÁCIL','INTERMEDIA','DIFÍCIL'][i],65,WHITE,True)
    title={'memory':'MEMORIZA','search':'¿CUÁL FALTA?','mask':'OJOS ATENTOS','answer':'LA RESPUESTA'}[phase]
    text(d,(90,465),title,57,WHITE,True)
    subtitle={'memory':f'Recuerda estos {len(r["objects"])} objetos.', 'search':'Uno desapareció. Encuéntralo.', 'mask':'Ahora cambia el orden…', 'answer':'Vuelve a mirar el conjunto completo.'}[phase]
    text(d,(90,548),subtitle,32,MUTED)
    if phase=='mask':
        d.rounded_rectangle((90,650,880,1330),radius=40,fill=PANEL)
        text(d,(485,950),'?',180,LIME,True,anchor='mm')
        text(d,(485,1150),'RECUERDA',39,WHITE,True,anchor='mm')
    else:
        items=r['objects'] if phase in ('memory','answer') else survivors(r)
        cols=2 if i<2 else 3; rows=math.ceil(len(r['objects'])/cols)
        cw=(790-(cols-1)*18)//cols; ch=225 if rows==3 else 295
        for j in range(len(r['objects'])):
            x=90+(j%cols)*(cw+18); y=650+(j//cols)*(ch+18)
            d.rounded_rectangle((x,y,x+cw,y+ch),radius=28,fill=PANEL)
            if j<len(items):
                name=items[j]; ix=x+(cw-164)//2; iy=y+(ch-164)//2
                im.paste(icon(name),(ix,iy),icon(name))
                if phase=='answer' and name==r['missing']:
                    d.rounded_rectangle((x+3,y+3,x+cw-3,y+ch-3),radius=26,outline=LIME,width=6)
        if phase=='answer':
            text(d,(90,1440),f'FALTABA: {NAMES[r["missing"]]}',48,LIME,True)
        else:
            text(d,(90,1440),'Guarda la imagen en tu memoria.' if phase=='memory' else 'Piensa antes de ver la solución.',32,MUTED)
    return im

def frame(t):
    i,phase,elapsed,duration=state(t); im=base(i,phase).copy(); d=ImageDraw.Draw(im)
    if phase not in ('intro','outro'):
        cx,cy=812,390
        d.ellipse((cx-50,cy-50,cx+50,cy+50),outline='#49405d',width=7)
        d.arc((cx-50,cy-50,cx+50,cy+50),-90,-90+360*max(.001,1-elapsed/duration),fill=LIME,width=7)
        text(d,(cx,cy-2),str(max(1,math.ceil(duration-elapsed))),40,WHITE,True,anchor='mm')
    d.rounded_rectangle((90,1564,880,1572),radius=4,fill='#403850')
    d.rounded_rectangle((90,1564,90+max(2,790*t/70),1572),radius=4,fill=LIME)
    return im

def verify_video(path,seconds):
    data=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(path)],text=True))
    v=data['streams']; assert len(v)==1 and v[0]['codec_type']=='video', 'Unexpected audio/streams'
    v=v[0]; assert (v['codec_name'],v['width'],v['height'],v['r_frame_rate'],v['pix_fmt'])==('h264',W,H,'30/1','yuv420p')
    assert int(v['nb_read_frames'])==round(seconds*FPS)
    assert abs(float(data['format']['duration'])-seconds)<.04
    subprocess.run(['ffmpeg','-v','error','-i',str(path),'-f','null','-'],check=True,timeout=180)
    return data

def render(seconds,output):
    validate_logic(); output.mkdir(parents=True,exist_ok=True)
    label='prueba-b-10s' if seconds==10 else 'piloto-001-v1'
    path=output/f'{label}.mp4'; assert not path.exists(), f'Refusing overwrite: {path}'
    command=['ffmpeg','-hide_banner','-loglevel','error','-n','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(path)]
    started=time.monotonic(); proc=subprocess.Popen(command,stdin=subprocess.PIPE)
    peaks={'sum_rss_bytes_sampled':0}; stop=threading.Event()
    def sample():
        parent=psutil.Process()
        while not stop.wait(.1):
            try:
                total=sum(p.memory_info().rss for p in [parent]+parent.children(recursive=True) if p.is_running())
                peaks['sum_rss_bytes_sampled']=max(peaks['sum_rss_bytes_sampled'],total)
            except psutil.Error: pass
    thread=threading.Thread(target=sample,daemon=True); thread.start()
    try:
        for index in range(round(seconds*FPS)):
            if time.monotonic()-started>900: raise TimeoutError('Local render exceeded 15-minute cap')
            proc.stdin.write(frame(index/FPS).tobytes())
        proc.stdin.close(); assert proc.wait(timeout=120)==0
    finally:
        if proc.poll() is None: proc.kill(); proc.wait()
        stop.set(); thread.join()
    render_seconds=round(time.monotonic()-started,3)
    probe=verify_video(path,seconds)
    metrics={'file':path.name,'status':'GENERATED_PENDING_REVIEW','duration_seconds':seconds,'frames':round(seconds*FPS),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'size_bytes':path.stat().st_size,'render_wall_seconds':render_seconds,'memory':peaks,'memory_method':'sum of Python and child process RSS sampled every 100 ms; shared pages may be counted twice; excludes verification','environment':'local Windows, not GitHub Actions','Pillow':PIL.__version__,'ffmpeg':subprocess.check_output(['ffmpeg','-version'],text=True).splitlines()[0],'probe':probe,'rounds':ROUNDS}
    assert peaks['sum_rss_bytes_sampled']<2*1024**3, 'RAM target exceeded'
    assert path.stat().st_size<1024**3, 'Output storage target exceeded'
    (output/f'{label}.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in metrics.items() if k not in ('probe','rounds')},ensure_ascii=False),flush=True)

def previews(output):
    output.mkdir(parents=True,exist_ok=True)
    stamps=[1,5,9.5,13,20,25,29.5,35,41,47,51.5,57,63,67]
    sheet=Image.new('RGB',(5*270,3*510),'#0b0b15'); d=ImageDraw.Draw(sheet)
    for index,t in enumerate(stamps):
        tile=frame(t).resize((270,480),Image.Resampling.LANCZOS); x=(index%5)*270;y=(index//5)*510
        sheet.paste(tile,(x,y)); d.text((x+12,y+483),f'{t:g} s / {state(t)[1]}',font=font(19),fill=WHITE)
    sheet.save(output/'storyboard.jpg',quality=92)
    frame(1).save(output/'portada-001.jpg',quality=95)
    for t in (5,13,20,35,41,57,63): frame(t).save(output/f'qa-{t:02d}s.png')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--seconds',type=int,choices=[10,70]);parser.add_argument('--previews',action='store_true');parser.add_argument('--output',type=Path,default=ROOT/'output/piloto-001-v1'); args=parser.parse_args()
    validate_logic()
    if args.previews: previews(args.output)
    if args.seconds: render(args.seconds,args.output)
    if not args.previews and not args.seconds: parser.error('Choose --previews or --seconds')
