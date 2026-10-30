"""Complete 70-second color memory challenge, approved avatar and Alex style. Local only."""
from pathlib import Path
from functools import lru_cache
import subprocess,json,math,time,hashlib
import numpy as np
import soundfile as sf
from PIL import Image,ImageDraw,ImageFont
import animate_natural as motion
from animate_natural import Morph,feather,cells,pulse
from animate_expressive import align

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'output/current'
OLD=V4=V5=NAT=ROOT/'assets/presenter'
FACE=(280,200,660,580)
COLORS={'amarillo':'#ffd52a','azul':'#48bcff','verde':'#6ee295','rojo':'#f45d70','rosa':'#ff9bcc','morado':'#c09bff','naranja':'#ffad5c','turquesa':'#48dce2'}
NAMES={'mug':'TAZA','key':'LLAVE','heart':'CORAZÓN','umbrella':'PARAGUAS','star':'ESTRELLA','leaf':'HOJA','gift':'REGALO','clock':'RELOJ'}
ROUNDS=[
 {'start':6,'mask':13,'search':14,'answer':20,'end':25,'items':[('mug','amarillo'),('key','verde'),('heart','rosa'),('umbrella','morado')],'target':'mug','new':'azul'},
 {'start':25,'mask':33,'search':34,'answer':40,'end':45,'items':[('star','rojo'),('leaf','amarillo'),('gift','morado'),('mug','azul'),('key','naranja'),('heart','rosa')],'target':'star','new':'verde'},
 {'start':45,'mask':54,'search':55,'answer':61,'end':66,'items':[('clock','azul'),('heart','rojo'),('umbrella','naranja'),('star','amarillo'),('leaf','verde'),('gift','morado'),('key','turquesa'),('mug','rosa')],'target':'clock','new':'rosa'},
]
PANEL=(154,615,567,945)
BASE=None
EPISODE=4

@lru_cache(maxsize=32)
def font(n):return ImageFont.truetype(str(ROOT/'assets/fonts/Barlow-Bold.ttf'),n)

def text(d,xy,s,n=25,color='white',anchor='mt'):
    d.text(xy,s,font=font(n),fill=color,anchor=anchor)

@lru_cache(maxsize=100)
def icon(name,color,size):
    im=Image.new('RGBA',(240,240));d=ImageDraw.Draw(im);c=COLORS[color];white='#edf6ff';bg='#12335b'
    if name=='mug':
        d.rounded_rectangle((155,75,222,169),radius=28,outline=c,width=20)
        d.rounded_rectangle((38,65,175,198),radius=21,fill=c)
        d.ellipse((38,54,175,82),fill=white);d.ellipse((52,61,161,74),fill=bg)
    elif name=='key':
        d.ellipse((27,22,132,127),outline=c,width=21)
        d.line((113,108,207,208),fill=c,width=25)
        d.line((158,157,184,130),fill=c,width=23);d.line((184,184,210,158),fill=c,width=23)
    elif name=='heart':
        d.ellipse((22,43,125,146),fill=c);d.ellipse((115,43,218,146),fill=c)
        d.polygon([(25,116),(120,211),(215,116)],fill=c)
    elif name=='umbrella':
        d.pieslice((16,35,224,214),180,360,fill=c)
        d.line((120,126,120,201),fill=white,width=13);d.arc((78,177,123,223),0,180,fill=white,width=12)
    elif name=='star':
        pts=[(120+99*math.cos(-math.pi/2+i*math.pi/5)*(1 if i%2==0 else .45),120+99*math.sin(-math.pi/2+i*math.pi/5)*(1 if i%2==0 else .45)) for i in range(10)]
        d.polygon(pts,fill=c)
    elif name=='leaf':
        d.ellipse((48,16,198,216),fill=c);d.line((66,219,170,57),fill=white,width=11)
        d.line((107,156,75,123),fill=white,width=8);d.line((135,118,177,113),fill=white,width=8)
    elif name=='gift':
        d.rounded_rectangle((39,85,201,215),radius=10,fill=c);d.rectangle((28,74,212,110),fill=c)
        d.rectangle((108,75,130,215),fill=white)
        d.ellipse((65,25,121,78),outline=white,width=12);d.ellipse((120,25,176,78),outline=white,width=12)
    elif name=='clock':
        d.ellipse((25,25,215,215),fill=c);d.ellipse((44,44,196,196),fill=bg)
        d.line((120,65,120,121,163,145),fill=white,width=12)
        for a in range(0,360,90):
            x,y=120+63*math.cos(math.radians(a)),120+63*math.sin(math.radians(a));d.ellipse((x-4,y-4,x+4,y+4),fill=white)
    else:raise ValueError(name)
    return im.resize((size,size),Image.Resampling.LANCZOS)

def state(t):
    if t<6:return -1,'intro',6
    for i,r in enumerate(ROUNDS):
        if r['start']<=t<r['end']:
            if t<r['mask']:return i,'memory',r['mask']
            if t<r['search']:return i,'mask',r['search']
            if t<r['answer']:return i,'search',r['answer']
            return i,'answer',r['end']
    return 3,'outro',70

def items(i,phase):
    r=ROUNDS[i]
    return [(name,r['new'] if phase in ['search','answer'] and name==r['target'] else color) for name,color in r['items']]

def slots(i):
    cols=[2,3,4][i];xs=[360+(j-(cols-1)/2)*(390/cols) for j in range(cols)]
    return [(round(xs[j%cols]),[743,862][j//cols]) for j in range(len(ROUNDS[i]['items']))]

@lru_cache(maxsize=150)
def board(i,phase,count):
    im=BASE.copy();d=ImageDraw.Draw(im)
    d.rectangle((0,0,720,173),fill='#062552')
    text(d,(360,22),f'RETO VISUAL 70 · RETO {EPISODE:03d}',29,'#ffdb36')
    text(d,(360,65),'¿QUÉ OBJETO',43)
    text(d,(360,111),'CAMBIÓ DE COLOR?',43)
    d.rounded_rectangle(PANEL,radius=15,fill='#12335b')
    d.rounded_rectangle((103,976,619,1116 if phase=='answer' else 1049),radius=17,fill='#062552')
    if phase=='intro':
        text(d,(360,636),'3 RONDAS · 4 / 6 / 8 OBJETOS',25,'#ffdb36')
        for y,line in [(712,'MEMORIZA LOS COLORES'),(778,'ENCUENTRA EL CAMBIO'),(844,'COMPRUEBA LA SOLUCIÓN')]:text(d,(360,y),line,25)
        text(d,(360,991),'Cada ronda cambia un solo color.',27)
    elif phase=='outro':
        text(d,(360,641),'RETO COMPLETADO',29,'#ffdb36')
        text(d,(360,720),'TU MARCADOR',29)
        text(d,(360,780),'0 · 1 · 2 · 3',60,'#ffdb36')
        text(d,(360,878),'¿CUÁNTAS ACERTASTE?',27)
        text(d,(360,991),'Escribe tu resultado en comentarios.',27)
    else:
        r=ROUNDS[i];before=dict(r['items'])[r['target']]
        text(d,(171,632),f'RONDA {i+1} · {len(r["items"])} OBJETOS',23,'#ffdb36','lt')
        if phase in ['memory','search']:text(d,(550,630),str(count),27,'#ffdb36','rt')
        title={'memory':'MEMORIZA','mask':'GUARDA LOS COLORES','search':'¿CUÁL CAMBIÓ?','answer':'SOLUCIÓN'}[phase]
        text(d,(360,665),title,27)
        if phase=='mask':
            text(d,(360,742),'?',100,'#ffdb36')
            text(d,(360,875),'RECUERDA…',25)
        else:
            size=[88,76,68][i];labelsize=[23,21,19][i]
            for (name,color),(x,y) in zip(items(i,phase),slots(i)):
                half=[67,53,44][i]
                highlighted=phase=='answer' and name==r['target']
                d.rounded_rectangle((x-half,y-49,x+half,y+65),radius=11,fill='#163e68',outline='#ffdb36' if highlighted else '#315778',width=4 if highlighted else 1)
                ico=icon(name,color,size);im.alpha_composite(ico,(x-size//2,y-size//2))
                fitted=labelsize
                while font(fitted).getlength(NAMES[name])>2*half-9:fitted-=1
                text(d,(x,y+43),NAMES[name],fitted)
        if phase=='answer':
            solution=f'{NAMES[r["target"]]}: {before.upper()} A {r["new"].upper()}'
            solution_size=28
            while font(solution_size).getlength(solution)>490:solution_size-=1
            text(d,(360,985),solution,solution_size,'#ffdb36')
            for x,c in [(285,before),(435,r['new'])]:
                d.rounded_rectangle((x-24,1022,x+24,1070),radius=8,fill=COLORS[c])
                text(d,(x,1075),c.upper(),21)
            d.line((341,1046,374,1046),fill='white',width=4)
            d.polygon([(374,1038),(386,1046),(374,1054)],fill='white')
        else:text(d,(360,991),{'memory':'Memoriza sin pausar.','mask':'Todo queda oculto antes del cambio.','search':'Solo cambió un color.'}[phase],26)
    text(d,(360,1161),'@retovisual70',25,'#cbdff2')
    return im

def validate_logic():
    assert [len(r['items']) for r in ROUNDS]==[4,6,8]
    for i,r in enumerate(ROUNDS):
        assert len(dict(r['items']))==len(r['items'])
        assert dict(r['items'])[r['target']]!=r['new']
        assert [n for n,c in items(i,'memory')]==[n for n,c in items(i,'search')]
        assert [n for (n,c),(_,c2) in zip(items(i,'memory'),items(i,'search')) if c!=c2]==[r['target']]
        assert r['search']-r['mask']==1 and r['end']-r['answer']==5
    assert ROUNDS[0]['start']==6 and ROUNDS[-1]['end']==66
    assert ROUNDS[0]['end']==ROUNDS[1]['start'] and ROUNDS[1]['end']==ROUNDS[2]['start']

def main(filename='reto-visual-70-video-002-color-v1-final.mp4'):
    global BASE
    validate_logic()
    dest=OUT/filename;assert not dest.exists()
    if not (OUT/'base-aprobada.png').exists():
        import shutil
        shutil.copyfile(V5/'base-aprobada.png',OUT/'base-aprobada.png')
    BASE=Image.open(OUT/'base-aprobada.png').convert('RGBA')
    # Registered face and geometry are exactly the approved v4 calibration; only
    # narration and corresponding motion curves are new for the actual challenge.
    av=Image.open(V4/'face-reference.png').convert('RGBA')
    ref=av.convert('RGB');alpha=av.getchannel('A')
    def registered(path):return [align(c,ref)[0] for c in cells(path)]
    nat=registered(NAT/'bocas-naturales-atlas.png');old=registered(OLD/'expresiones-atlas.png')
    mouthbox=(83,181,298,298);eyebox=(46,85,334,169);browbox=(63,44,317,94)
    slight=Morph(nat[1].crop(mouthbox),nat[2].crop(mouthbox)).at(.18)
    intermediate=Morph(nat[2].crop(mouthbox),old[1].crop(mouthbox)).at(.78)
    rounded=Morph(nat[3].crop(mouthbox),old[2].crop(mouthbox)).at(.50)
    m01=Morph(ref.crop(mouthbox),slight);m12=Morph(slight,intermediate)
    eyes=Morph(ref.crop(eyebox),old[3].crop(eyebox));brows=Morph(ref.crop(browbox),old[2].crop(browbox))
    masks={b:feather((b[2]-b[0],b[3]-b[1])) for b in [mouthbox,eyebox,browbox]}
    wav=OUT/'narracion-final.wav';wave,rate=sf.read(wav,dtype='float32');assert rate==24000 and len(wave)==70*rate
    narration=json.loads((OUT/'narracion.json').read_text(encoding='utf-8'))
    motion.N=2100;rows=motion.controls(wave,narration['sentences'])
    for row in rows:
        t=row['t'];row['blink']=max(pulse(t,c) for c in [1.27,4.34,8.36,12.4,17.3,22.7,28.4,32.6,37.2,42.5,48.4,52.6,57.8,63.4,68.2])
        row['brow']=sum(.23*math.exp(-.5*((t-c)/.35)**2) for c in [1.,14.5,20.5,34.5,40.5,55.5,61.5,67.])
    started=time.monotonic();round_cache={};face_cache={};saved=[]
    proc=subprocess.Popen(['ffmpeg','-v','error','-n','-f','rawvideo','-pix_fmt','rgb24','-s','720x1280','-r','30','-i','pipe:0','-i',str(wav),'-vf','scale=1080:1920:flags=lanczos,setsar=1','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-t','70','-movflags','+faststart',str(dest)],stdin=subprocess.PIPE)
    sample_times=[2,8,13.5,16,22,27,33.5,36,42,48,54.5,57,63,68]
    try:
        for n,row in enumerate(rows):
            t=n/30;i,phase,end=state(t);count=max(1,math.ceil(end-t))
            im=board(i,phase,count).copy()
            j=min(.95,row['jaw']*1.20)
            # Fine temporal cache preserves smooth variation, not discrete visemes.
            key=(round(j*120),round(row['rounding']*120),round(row['blink']*60),round(row['brow']*120))
            if key not in face_cache:
                face=ref.copy();mouth=m01.at(j/.34) if j<=.34 else m12.at((j-.34)/.66)
                if row['rounding']>.005 and j>.04:
                    k=round(j*60)
                    if k not in round_cache:
                        anchor=m01.at(k/60/.34) if k/60<=.34 else m12.at((k/60-.34)/.66)
                        round_cache[k]=Morph(anchor,rounded)
                    mouth=round_cache[k].at(row['rounding']*.65*min(1,j/.25))
                face.paste(mouth,mouthbox[:2],masks[mouthbox])
                face.paste(eyes.at(row['blink']),eyebox[:2],masks[eyebox])
                face.paste(brows.at(row['brow']),browbox[:2],masks[browbox])
                layer=face.convert('RGBA');layer.putalpha(alpha)
                face_cache[key]=layer.resize((241,241),Image.Resampling.LANCZOS)
            im.alpha_composite(face_cache[key],(217,272))
            rgb=im.convert('RGB');proc.stdin.write(rgb.tobytes())
            if any(n==round(st*30) for st in sample_times):
                filename=f'frame-disenado-{n:04d}.png';rgb.resize((1080,1920),Image.Resampling.LANCZOS).save(OUT/filename);saved.append({'frame':n,'t':t,'state':[i,phase,count],'path':filename})
            if n%300==0:print(f'Render {n}/2100',flush=True)
    finally:proc.stdin.close()
    assert proc.wait()==0
    record={'status':'GENERATED_PENDING_FULL_QA','seconds':70,'fps':30,'frames':2100,'size':[1080,1920],'voice':'em_alex .96; new narration','mouth':'Approved v4 range and optical-flow calibration; new audio-driven curves','pose':'Approved v5 hugging panel','music':False,'rounds':ROUNDS,'samples':saved,'render_seconds':round(time.monotonic()-started,2),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'publication':False,'scheduled':False}
    (OUT/'manifest.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'controles.json').write_text(json.dumps(rows),encoding='utf-8')
    print(json.dumps(record,ensure_ascii=False),flush=True)

if __name__=='__main__':main()
