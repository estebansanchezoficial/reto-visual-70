"""Portable, deterministic daily challenge. Every output still needs approval."""
from datetime import date
from pathlib import Path
import argparse, hashlib, json, random
import second_video as video

ARTICLES={'mug':'La taza','key':'La llave','heart':'El corazón','umbrella':'El paraguas','star':'La estrella','leaf':'La hoja','gift':'El regalo','clock':'El reloj'}

def plan(day):
    day=date.fromisoformat(day)
    assert day>=date(2026,11,1), 'Videos 001–003 are protected'
    episode=4+(day-date(2026,11,1)).days
    rng=random.Random('rv70-daily-color-v1:'+day.isoformat())
    names=list(video.NAMES); colors=list(video.COLORS)
    rounds=[];answers=[]
    for count,timing in zip([4,6,8],[(6,13,14,20,25),(25,33,34,40,45),(45,54,55,61,66)]):
        rng.shuffle(names);rng.shuffle(colors)
        items=list(zip(names[:count],colors[:count]));target=rng.choice(items)
        new=rng.choice([c for c in colors if c!=target[1]])
        rounds.append(dict(zip(['start','mask','search','answer','end'],timing),items=items,target=target[0],new=new))
        answers.append(f'{ARTICLES[target[0]]} cambió de {target[1]} a {new}.')
    return {'date':day.isoformat(),'episode':episode,'rounds':rounds,'answer_texts':answers,'scheduled':False,'published':False,'ai_label':True,'music':'Inside Algorithm — Cool Ember Sync; add in TikTok only; -24 dB; fades 1 s / 2 s','publication_target':f'{day.isoformat()} 19:00 America/Mexico_City'}

def main(day):
    import second_narration as voice
    import verify
    data=plan(day);out=video.ROOT/'output/current'
    out.mkdir(parents=True,exist_ok=True)
    assert not (out/'plan.json').exists(), 'Do not overwrite an existing package'
    for name,sha in json.loads((video.ROOT/'assets/presenter/sha256.json').read_text()).items():
        assert hashlib.sha256((video.ROOT/'assets/presenter'/name).read_bytes()).hexdigest()==sha
    (out/'plan.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    video.OUT=voice.OUT=out;video.ROUNDS=data['rounds'];video.EPISODE=data['episode']
    for i in range(3):
        key=f'answer{i+1}';_,start,limit=voice.PHRASES[key]
        voice.PHRASES[key]=(data['answer_texts'][i],start,limit)
    voice.main()
    video.main('video.mp4')
    verify.OUT=out;verify.VIDEO=out/'video.mp4';verify.main()
    caption='¿Detectas los tres cambios de color? Sin pausar: memoriza, encuentra y comprueba. ¿Cuántas acertaste? #RetoVisual70 #RetoVisual #MemoriaVisual #Acertijos #EntrenaTuMente'
    (out/'descripcion.txt').write_text(caption+'\n',encoding='utf-8')
    return data

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--date',required=True)
    main(parser.parse_args().date)
