"""Synthesize a new, timed Alex narration for the second video; no publication."""
import os
os.environ.setdefault('OMP_NUM_THREADS','2')
os.environ.setdefault('OPENBLAS_NUM_THREADS','2')
from pathlib import Path
import hashlib,json,subprocess,time
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro
from misaki.espeak import EspeakG2P
from phonemizer.backend.espeak.wrapper import EspeakWrapper
import espeakng_loader

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'output/current'
OUT.mkdir(exist_ok=True,parents=True)
PHRASES={
 'hook':('¿Qué objeto cambió de color?',.25,2.5),
 'rules':('Memoriza, y encuentra el cambio.',2.85,2.9),
 'round1':('Ronda uno. Cuatro objetos.',6.15,3.2),
 'find':('¿Cuál cambió?',14.15,2.0),
 'answer1':('La taza cambió de amarillo a azul.',20.2,4.5),
 'round2':('Ronda dos. Seis objetos.',25.15,3.2),
 'answer2':('La estrella cambió de rojo a verde.',40.2,4.5),
 'round3':('Última ronda. Ocho objetos.',45.15,3.2),
 'answer3':('El reloj cambió de azul a rosa.',61.2,4.5),
 'outro':('¿Cuántas acertaste? Escribe tu resultado.',66.05,3.85),
}

def main():
    assert not (OUT/'narracion-70s.wav').exists(),'Keep existing narration'
    model=ROOT/'output/models/kokoro-v1.0.onnx'
    voices=ROOT/'output/models/voices-v1.0.bin'
    for p,sha in [(model,'7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5'),(voices,'bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d')]:
        with p.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==sha
    EspeakWrapper.set_library(espeakng_loader.get_library_path())
    engine=Kokoro(str(model),str(voices));g2p=EspeakG2P(language='es')
    rate=24000;full=np.zeros(70*rate,np.float32);events=[];started=time.monotonic()
    for ident,(text,start,limit) in PHRASES.items():
        saved=OUT/f'voz-{ident}.wav';meta=OUT/f'voz-{ident}.json'
        if saved.exists():
            audio,r=sf.read(saved,dtype='float32');entry=json.loads(meta.read_text(encoding='utf-8'));assert entry['text']==text and r==rate
        else:
            phonemes,_=g2p(text)
            audio,r=engine.create(phonemes,'em_alex',speed=.96,is_phonemes=True,trim=True,sentence_pause=.12,clause_pause=0.0)
            assert r==rate
            entry={'id':ident,'text':text,'phonemes':phonemes,'duration':len(audio)/rate}
            sf.write(saved,audio,rate,subtype='PCM_16');meta.write_text(json.dumps(entry,ensure_ascii=False,indent=2),encoding='utf-8')
        assert entry['duration']<=limit,(ident,entry['duration'],limit)
        times=[start] if ident!='find' else [14.15,34.15,55.15]
        for at in times:
            pos=round(at*rate);end=pos+len(audio)
            assert end<=len(full) and not np.any(full[pos:end])
            full[pos:end]=audio
            events.append({**entry,'start':at,'pause':0.})
        print(json.dumps({'voice_clip':ident,'seconds':round(entry['duration'],3),'text':text},ensure_ascii=False),flush=True)
    sf.write(OUT/'narracion-70s.wav',full,rate,subtype='PCM_16')
    subprocess.run(['ffmpeg','-v','error','-n','-i',str(OUT/'narracion-70s.wav'),'-af','loudnorm=I=-16:TP=-1.5:LRA=7','-ar','24000','-c:a','pcm_s16le',str(OUT/'narracion-final.wav')],check=True)
    rec={'voice':'em_alex','speed':.96,'language':'es','duration':70,'sentences':sorted(events,key=lambda e:e['start']),'generation_seconds':round(time.monotonic()-started,2),'music':False}
    (OUT/'narracion.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Narration complete',flush=True)

if __name__=='__main__':main()
