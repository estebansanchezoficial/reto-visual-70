"""Different challenge mechanics within the approved presenter composition."""
from functools import lru_cache
import hashlib,json
from PIL import ImageDraw
import numpy as np
import second_video as video

FAMILIES=['arithmetic','vowels','color','pattern']
WORDS=['CAMINO','VENTANA','MARIPOSA','BIBLIOTECA','TELEFONO','CARACOL','UNIVERSO','PRIMAVERA','ELEFANTE','CHOCOLATE','MURCIELAGO','CUADERNO','ESTRELLA','PLANETA','SEMILLA','GIRASOL','ESCUELA','AEROPUERTO','AVENTURA','NATURALEZA','CARRETERA','MONEDA','ESTUDIANTE','ROMPECABEZAS']
TITLES={'arithmetic':'¿CUÁNTO DA?','vowels':'¿CUÁNTAS VOCALES?','pattern':'¿QUÉ FIGURA SIGUE?'}
DATA=None

def fingerprint(data):
    family=data.get('family','color')
    if family=='arithmetic':content=[(sorted([r['a'],r['b']]) if r['op']=='+' else [r['a'],r['b']],r['op']) for r in data['rounds']]
    elif family=='vowels':content=[r['word'] for r in data['rounds']]
    elif family=='pattern':
        names={'circle':'CÍRCULO','triangle':'TRIÁNGULO','square':'CUADRADO'}
        content=[([names.get(v,v) for v in r['sequence']],names.get(r['next'],r['next'])) for r in data['rounds']]
    else:content=[(sorted(r['items']),r['target'],r['new']) for r in data['rounds']]
    content=sorted(content,key=lambda value:json.dumps(value,ensure_ascii=False,sort_keys=True))
    return hashlib.sha256(json.dumps([family,content],ensure_ascii=False,sort_keys=True).encode()).hexdigest()

def recent_families(history,episode):
    latest={}
    for entry in history:
        n=entry.get('episode',0)
        if n>=episode:continue
        if n not in latest or entry.get('revision',1)>latest[n].get('revision',1):latest[n]=entry
    return [latest[n].get('family','color') for n in sorted(latest)[-2:]]

def compare(data,history,rejected_family=None):
    recent=recent_families(history,data['episode'])
    assert data['family'] not in recent, f'Too similar: challenge family already in preceding two videos: {recent}'
    assert data['family']!=rejected_family, 'Correction must change the rejected challenge mechanic'
    signature=fingerprint(data)
    assert signature not in [fingerprint(h) for h in history], 'Repeated puzzle content'
    return {'status':'PASS','policy':'Different mechanic from previous two episodes and rejected version; no identical canonical puzzles or MP4 SHA-256. Presenter/voice template may repeat.','family':data['family'],'recent_families':recent,'content_sha256':signature,'compared':[{'episode':h.get('episode'),'revision':h.get('revision',1),'family':h.get('family','color'),'sha256':h.get('sha256'),'content_sha256':fingerprint(h)} for h in history]}

def make_rounds(family,rng):
    rounds=[];used_words=rng.sample(WORDS,3)
    for i,(start,answer,end) in enumerate([(6,20,25),(25,40,45),(45,61,66)]):
        r={'start':start,'answer':answer,'end':end}
        if family=='arithmetic':
            a=rng.randint(3+3*i,12+6*i);b=rng.randint(2,8+3*i)
            op=rng.choice(['+','-']) if i else '+'
            if op=='-' and b>=a:a,b=max(a,b)+3,min(a,b)
            expected=a+b if op=='+' else a-b
            r.update(a=a,b=b,op=op,next=expected,explanation=f'{a} {op} {b} = {expected}')
        elif family=='vowels':
            word=used_words[i];expected=sum(c in 'AEIOU' for c in word)
            r.update(word=word,next=expected,explanation=' · '.join(c for c in word if c in 'AEIOU'))
        elif family=='pattern':
            a,b,c=rng.sample(['CÍRCULO','TRIÁNGULO','CUADRADO'],3)
            pattern=[a,b] if i==0 else ([a,a,b] if i==1 else [a,b,c])
            seq=[pattern[j%len(pattern)] for j in range(4 if i!=1 else 5)]
            expected=pattern[len(seq)%len(pattern)]
            r.update(sequence=seq,pattern=pattern,next=expected,explanation=' · '.join(pattern))
        else:raise ValueError(family)
        choices=([expected,expected+1,max(0,expected-1)] if isinstance(expected,int) else ['CÍRCULO','TRIÁNGULO','CUADRADO'])
        rng.shuffle(choices);r.update(choices=choices,correct=choices.index(expected))
        rounds.append(r)
    return rounds

def validate(data):
    for r in data['rounds']:
        if data['family']=='arithmetic':expected=r['a']+r['b'] if r['op']=='+' else r['a']-r['b']
        elif data['family']=='vowels':expected=sum(c in 'AEIOU' for c in r['word'])
        elif data['family']=='pattern':
            assert r['sequence']==[r['pattern'][i%len(r['pattern'])] for i in range(len(r['sequence']))]
            expected=r['pattern'][len(r['sequence'])%len(r['pattern'])]
        else:raise ValueError(data['family'])
        assert r['next']==expected and r['choices'][r['correct']]==expected
        assert len(set(r['choices']))==3 and r['end']-r['answer']==5

def state(t):
    if t<6:return -1,'intro',6
    for i,r in enumerate(DATA['rounds']):
        if r['start']<=t<r['answer']:return i,'puzzle',r['answer']
        if r['answer']<=t<r['end']:return i,'answer',r['end']
    return 3,'outro',70

def fit(d,xy,text,size,width=490,color='white'):
    while video.font(size).getlength(text)>width:size-=1
    video.text(d,xy,text,size,color)

def shape(im,value,x,y,size=42):
    d=ImageDraw.Draw(im);h=size/2
    if value=='CÍRCULO':d.ellipse((x-h,y-h,x+h,y+h),fill='#48dce2')
    elif value=='TRIÁNGULO':d.polygon([(x,y-h),(x-h,y+h),(x+h,y+h)],fill='#ffd52a')
    else:d.rounded_rectangle((x-h,y-h,x+h,y+h),radius=5,fill='#ff9bcc')

@lru_cache(maxsize=150)
def board(i,phase,count):
    im=video.BASE.copy();d=ImageDraw.Draw(im);family=DATA['family']
    d.rectangle((0,0,720,173),fill='#062552')
    fit(d,(360,22),f"RETO VISUAL 70 · RETO {DATA['episode']:03d}",29,color='#ffdb36')
    fit(d,(360,73),TITLES[family],43,width=650)
    video.text(d,(360,126),'3 RONDAS · ELIGE A, B O C',28,'#cfdfef')
    d.rounded_rectangle(video.PANEL,radius=15,fill='#12335b')
    d.rounded_rectangle((103,976,619,1116 if phase=='answer' else 1049),radius=17,fill='#062552')
    if phase=='intro':
        video.text(d,(360,642),'ACEPTA EL RETO',30,'#ffdb36')
        fit(d,(360,735),{'arithmetic':'NÚMEROS EN ACCIÓN','vowels':'OBSERVA CADA PALABRA','pattern':'DESCUBRE EL PATRÓN'}[family],31,width=380)
        video.text(d,(360,809),'PIENSA · ELIGE · COMPRUEBA',23)
        video.text(d,(360,875),'A · B · C',43,'#ffdb36')
        video.text(d,(360,991),'Cada solución se explica completa.',26)
    elif phase=='outro':
        video.text(d,(360,642),'RETO COMPLETADO',30,'#ffdb36')
        video.text(d,(360,739),'TU MARCADOR',29)
        video.text(d,(360,800),'0 · 1 · 2 · 3',58,'#ffdb36')
        video.text(d,(360,884),'¿CUÁNTAS ACERTASTE?',26)
        video.text(d,(360,991),'Escribe tu resultado en comentarios.',27)
    else:
        r=DATA['rounds'][i];answer=phase=='answer'
        video.text(d,(171,632),f'RONDA {i+1}',23,'#ffdb36','lt')
        if not answer:video.text(d,(550,630),str(count),27,'#ffdb36','rt')
        video.text(d,(360,669),'SOLUCIÓN' if answer else TITLES[family],25)
        if family=='arithmetic':
            fit(d,(360,724),f"{r['a']} {r['op']} {r['b']} = {r['next'] if answer else '?'}",57,width=380)
        elif family=='vowels':fit(d,(360,729),r['word'],45,width=380,color='#48dce2')
        else:
            values=r['sequence']+[r['next'] if answer else '?'];step=380/len(values)
            for j,value in enumerate(values):
                x=360+(j-(len(values)-1)/2)*step
                if value=='?':video.text(d,(x,710),'?',49,'#ffdb36')
                else:shape(im,value,x,739,38)
        for k,(x,value) in enumerate(zip([245,360,475],r['choices'])):
            good=answer and k==r['correct']
            d.rounded_rectangle((x-46,817,x+46,934),radius=10,fill='#163e68',outline='#ffdb36' if good else '#315778',width=4 if good else 1)
            if family=='pattern':shape(im,value,x,857,43)
            else:video.text(d,(x,827),str(value),45)
            video.text(d,(x,901),'ABC'[k],25,'#ffdb36' if good else 'white')
        if answer:
            fit(d,(360,985),f"RESPUESTA {'ABC'[r['correct']]} · {r['next']}",28,color='#ffdb36')
            fit(d,(360,1032),r['explanation'],26)
            if family=='vowels':video.text(d,(360,1075),'Cada aparición de A, E, I, O, U cuenta.',23)
            elif family=='pattern':video.text(d,(360,1075),'Este grupo se repite en orden.',25)
        else:video.text(d,(360,991),'Piensa y elige antes de la solución.',27)
    video.text(d,(360,1161),'@retovisual70',25,'#cbdff2')
    return im

def verify_rendered(actual,data):
    checks=[]
    for i,(before,after) in enumerate([(8.,22.),(27.,42.),(48.,63.)]):
        diffs=[]
        for x in [245,360,475]:
            box=tuple(round(v*1.5) for v in (x-46,817,x+46,934))
            a=np.asarray(actual[before].crop(box),dtype=float);b=np.asarray(actual[after].crop(box),dtype=float)
            diffs.append(float(np.abs(a-b).mean()))
        changed=[j for j,e in enumerate(diffs) if e>4]
        assert changed==[data['rounds'][i]['correct']],diffs
        checks.append({'round':i+1,'highlighted_answer':'ABC'[changed[0]],'choice_differences':diffs,'answer_seconds':5})
    return checks
