"""Portable, deterministic daily challenge. Every output still needs approval."""
from datetime import date
from pathlib import Path
import argparse, hashlib, json, random
import second_video as video
import challenges
import catalog
import procedure

ARTICLES={'mug':'La taza','key':'La llave','heart':'El corazón','umbrella':'El paraguas','star':'La estrella','leaf':'La hoja','gift':'El regalo','clock':'El reloj'}

def plan(day,revision=1,history=None,rejected_family=None,requested_family=None):
    day=date.fromisoformat(day)
    assert day>=date(2026,11,1), 'Videos 001–003 are protected'
    episode=4+(day-date(2026,11,1)).days
    history=history if history is not None else json.loads((video.ROOT/'daily/content-history.json').read_text(encoding='utf-8'))
    if requested_family in (None,'catalog_math','arithmetic'):
        pack=catalog.select(history,rejected_family)
        rounds=pack['rounds']
        for r,timing in zip(rounds,[(6,20,25),(25,40,45),(45,61,66)]):
            r.update(zip(['start','answer','end'],timing))
        answers=[f"La {'ABC'[r['correct']]}. {r['spoken_answer']}" for r in rounds]
        data={'date':day.isoformat(),'episode':episode,'revision':revision,'family':'catalog_'+pack['topic'],
              'catalog_version':1,'pack_id':pack['pack_id'],'topic_title':pack['title'],'rounds':rounds,
              'answer_texts':answers,'scheduled':False,'published':False,'ai_label':True,
              'music':'Cipher — Kevin MacLeod; CC BY 4.0; embedded after voice QA',
              'publication_target':f'{day.isoformat()} 19:00 America/Mexico_City'}
        procedure.apply(data)
        challenges.compare(data,history,rejected_family);challenges.validate(data)
        return data
    forbidden=set(challenges.recent_families(history,episode))|{rejected_family}
    order=challenges.FAMILIES[(episode-4)%4:]+challenges.FAMILIES[:(episode-4)%4]
    family=requested_family or next(f for f in order if f not in forbidden)
    assert family not in forbidden, 'Requested mechanic too similar to recent/rejected videos'
    rng=random.Random(f'rv70-daily-mixed-v2:{day.isoformat()}:{revision}')
    names=list(video.NAMES); colors=list(video.COLORS)
    rounds=[];answers=[]
    for count,timing in zip([4,6,8],[(6,13,14,20,25),(25,33,34,40,45),(45,54,55,61,66)]) if family=='color' else []:
        rng.shuffle(names);rng.shuffle(colors)
        items=list(zip(names[:count],colors[:count]));target=rng.choice(items)
        new=rng.choice([c for c in colors if c!=target[1]])
        rounds.append(dict(zip(['start','mask','search','answer','end'],timing),items=items,target=target[0],new=new))
        answers.append(f'{ARTICLES[target[0]]} cambió de {target[1]} a {new}.')
    if family!='color':
        rounds=challenges.make_rounds(family,rng)
        for r in rounds:
            letter='ABC'[r['correct']]
            if family=='arithmetic':answers.append(f"La {letter}. {r['a']} {'más' if r['op']=='+' else 'menos'} {r['b']} son {r['next']}.")
            elif family=='vowels':answers.append(f"La {letter}. {r['word'].lower()} tiene {r['next']} vocales.")
            else:answers.append(f"La {letter}. Sigue {r['next'].lower()}. El grupo se repite.")
    data={'date':day.isoformat(),'episode':episode,'revision':revision,'family':family,'rounds':rounds,'answer_texts':answers,'scheduled':False,'published':False,'ai_label':True,'music':'Inside Algorithm — Cool Ember Sync; add in TikTok only; -24 dB; fades 1 s / 2 s','publication_target':f'{day.isoformat()} 19:00 America/Mexico_City'}
    challenges.compare(data,history,rejected_family)
    if family!='color':challenges.validate(data)
    return data

def main(day,revision=1,history_path=None,rejected_family=None,requested_family=None,output_dir=None):
    import second_narration as voice
    import verify
    history=json.loads(Path(history_path or video.ROOT/'daily/content-history.json').read_text(encoding='utf-8'))
    data=plan(day,revision,history,rejected_family,requested_family);out=Path(output_dir) if output_dir else video.ROOT/'output/current'
    out.mkdir(parents=True,exist_ok=True)
    assert not (out/'plan.json').exists(), 'Do not overwrite an existing package'
    for name,sha in json.loads((video.ROOT/'assets/presenter/sha256.json').read_text()).items():
        assert hashlib.sha256((video.ROOT/'assets/presenter'/name).read_bytes()).hexdigest()==sha
    (out/'plan.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    comparison=challenges.compare(data,history,rejected_family)
    (out/'comparison.json').write_text(json.dumps(comparison,ensure_ascii=False,indent=2),encoding='utf-8')
    video.OUT=voice.OUT=out;video.ROUNDS=data['rounds'];video.EPISODE=data['episode']
    video.DURATION=voice.DURATION=data.get('duration_seconds',70)
    video.SAMPLE_TIMES=procedure.samples(data) if data.get('procedure_version') else None
    for i in range(3):
        key=f'answer{i+1}';_,start,limit=voice.PHRASES[key]
        voice.PHRASES[key]=(data['answer_texts'][i],start,limit)
    if data['family']!='color':
        hook='Tres niveles de matemáticas.' if data.get('catalog_version') else {'arithmetic':'¿Puedes resolver estos cálculos?','vowels':'¿Cuántas vocales tiene cada palabra?','pattern':'¿Qué figura sigue?'}[data['family']]
        voice.PHRASES.update(hook=(hook,.25,2.8),rules=('Elige A, B o C. Comprueba tu respuesta.',3.1,2.8),round1=('Nivel básico.',6.15,3.2),round2=('Nivel intermedio.',25.15,3.2),round3=('Nivel avanzado.',45.15,3.2),find=('Elige tu respuesta.',14.15,2.0))
        challenges.DATA=data;challenges.board.cache_clear()
        video.state=challenges.state;video.board=challenges.board;video.validate_logic=lambda:challenges.validate(data)
    if data.get('procedure_version'):
        # Keep all speech inside its own round after extending the timeline.
        voice.PHRASES.pop('find',None)
        for i,r in enumerate(data['rounds'],1):
            voice.PHRASES[f'round{i}']=(f"Nivel {['básico','intermedio','avanzado'][i-1]}.",r['start']+.15,3.2)
            voice.PHRASES[f'find{i}']=('Elige tu respuesta.',r['answer']-5.85,2.)
            voice.PHRASES[f'answer{i}']=(data['answer_texts'][i-1],r['answer']+.2,4.5)
            voice.PHRASES[f'procedure{i}']=('Este es el procedimiento. Sigue los pasos en pantalla.',r['procedure_start']+.2,5.)
        voice.PHRASES['outro']=('¿Cuántas acertaste? Escribe tu resultado.',data['rounds'][-1]['end']+.05,3.85)
    voice.main()
    video.main('video.mp4')
    verify.OUT=out;verify.VIDEO=out/'video.mp4';verify.main()
    sha=json.loads((out/'verificacion-final.json').read_text())['sha256']
    assert sha not in [h.get('sha256') for h in history], 'Exact video already exists'
    comparison['video_sha256']=sha;comparison['exact_video_duplicate']=False
    (out/'comparison.json').write_text(json.dumps(comparison,ensure_ascii=False,indent=2),encoding='utf-8')
    lead=(data['topic_title']+': básico, intermedio y avanzado.') if data.get('catalog_version') else {'arithmetic':'Tres cálculos, tres oportunidades.','vowels':'Cuenta las vocales: cada aparición cuenta.','pattern':'Descubre la regla de cada secuencia.','color':'¿Detectas los tres cambios de color?'}[data['family']]
    caption=f"{lead} ¿Cuántas acertaste? #RetoVisual70 #RetoVisual #Acertijos #EntrenaTuMente"
    (out/'descripcion.txt').write_text(caption+'\n',encoding='utf-8')
    import music
    music.mix(out)
    return data

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--date',required=True);parser.add_argument('--revision',type=int,default=1);parser.add_argument('--history');parser.add_argument('--rejected-family');parser.add_argument('--family');parser.add_argument('--output')
    args=parser.parse_args();main(args.date,args.revision,args.history,args.rejected_family,args.family,args.output)
