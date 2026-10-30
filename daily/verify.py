"""Decode and inspect the real delivered MP4, including changes, speech and masking."""
from pathlib import Path
import subprocess,json,re,hashlib
import numpy as np
from PIL import Image,ImageDraw
import second_video as design

OUT=design.OUT
VIDEO=OUT/'video.mp4'

def main():
    meta=json.loads((OUT/'manifest.json').read_text(encoding='utf-8'))
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(VIDEO)],text=True))
    v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio')
    assert (v['width'],v['height'],v['nb_frames'],v['avg_frame_rate'],v['codec_name'],v['pix_fmt'])==(1080,1920,'2100','30/1','h264','yuv420p')
    assert a['codec_name']=='aac' and abs(float(probe['format']['duration'])-70)<.02
    subprocess.run(['ffmpeg','-v','error','-i',str(VIDEO),'-f','null','-'],check=True)
    qa=OUT/'revision';qa.mkdir(exist_ok=True)
    indices=[s['frame'] for s in meta['samples']]
    filt='select='+ '+'.join(f'eq(n\\,{n})' for n in indices)
    subprocess.run(['ffmpeg','-v','error','-n','-i',str(VIDEO),'-vf',filt,'-fps_mode','vfr',str(qa/'frame-%02d.png')],check=True)
    actual={};comparisons=[]
    sheet=Image.new('RGB',(1080,1920));draw=ImageDraw.Draw(sheet)
    for i,s in enumerate(meta['samples']):
        im=Image.open(qa/f'frame-{i+1:02d}.png').convert('RGB');actual[s['t']]=im
        expected=Image.open(OUT/s['path']).convert('RGB')
        delta=float(np.abs(np.asarray(im,dtype=float)-np.asarray(expected,dtype=float)).mean())
        assert delta<3.,(s['t'],delta)
        comparisons.append({'t':s['t'],'mean_RGB_error':round(delta,4)})
        sheet.paste(im.resize((270,480)),((i%4)*270,(i//4)*480))
    sheet.save(OUT/'revision.jpg',quality=95)
    actual[8.].save(OUT/'portada.jpg',quality=96)
    actual[2.].save(OUT/'vista-previa.jpg',quality=96)
    roundchecks=[]
    for i,(mt,st) in enumerate([(8.,16.),(27.,36.),(48.,57.)]):
        am=np.asarray(actual[mt],dtype=float);bs=np.asarray(actual[st],dtype=float)
        details=[];changed=[]
        size=[88,76,68][i]
        for (name,color),(x,y) in zip(design.ROUNDS[i]['items'],design.slots(i)):
            box=(round((x-size/2)*1.5),round((y-size/2)*1.5),round((x+size/2)*1.5),round((y+size/2)*1.5))
            x0,y0,x1,y1=box;error=float(np.abs(am[y0:y1,x0:x1]-bs[y0:y1,x0:x1]).mean())
            if error>5:changed.append(name)
            details.append({'object':name,'difference':round(error,4)})
        assert changed==[design.ROUNDS[i]['target']],details
        assert all(d['difference']<3 for d in details if d['object']!=design.ROUNDS[i]['target'])
        roundchecks.append({'round':i+1,'changed_objects':changed,'details':details,'fully_hidden_seconds':1,'answer_seconds':5})
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(VIDEO),'-vn','-f','f32le','-ac','1','-ar','24000','pipe:1'])
    sound=np.frombuffer(raw,dtype='<f4');assert abs(len(sound)/24000-70)<.05
    narration=json.loads((OUT/'narracion.json').read_text(encoding='utf-8'))
    speech=[]
    for event in narration['sentences']:
        seg=sound[round((event['start']+.08)*24000):round((event['start']+event['duration']-.08)*24000)]
        rms=float(np.sqrt(np.mean(seg**2)));assert rms>.02
        speech.append({'id':event['id'],'start':event['start'],'duration':event['duration'],'rms':round(rms,5)})
    silences=[]
    for start,end in [(9,12.7),(28,32.7),(48,53.7),(15.5,19.7),(35.5,39.7),(56.5,60.7)]:
        seg=sound[round(start*24000):round(end*24000)];rms=float(np.sqrt(np.mean(seg**2)));assert rms<.002,(start,rms)
        silences.append({'start':start,'end':end,'rms':rms})
    peak=float(np.max(np.abs(sound)));assert peak<1
    # Whole-frame black detection is distinct from the intentionally masked board.
    black=subprocess.run(['ffmpeg','-hide_banner','-i',str(VIDEO),'-vf','blackdetect=d=0.1:pic_th=0.98:pix_th=0.03','-an','-f','null','-'],capture_output=True,text=True,check=True)
    assert 'black_start:' not in black.stderr
    expected_text=json.loads((OUT/'plan.json').read_text(encoding='utf-8'))['answer_texts']
    assert [e['text'] for e in narration['sentences'] if e['id'].startswith('answer')]==expected_text
    result={'status':'PASS_PENDING_USER_APPROVAL','duration':70,'frames':2100,'size':[1080,1920],'fps':30,'video_codec':'H.264/yuv420p','audio_codec':'AAC','full_decode':True,'frame_comparisons':comparisons,'actual_video_round_checks':roundchecks,'narrated_segments':speech,'silence_checks':silences,'audio_peak':peak,'black_frames_detected':False,'sha256':hashlib.sha256(VIDEO.read_bytes()).hexdigest(),'bytes':VIDEO.stat().st_size,'scheduled':False,'published':False,'limits':'Technical and frame-based checks; final subjective review by user pending. Approximate audio-driven mouth motion, not phoneme-forced alignment. No TikTok account preview performed.'}
    (OUT/'verificacion-final.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    meta['status']='VERIFIED_PENDING_USER_APPROVAL';meta['verification']='verificacion-final.json';(OUT/'manifest.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['status','duration','frames','size','audio_peak','sha256','bytes','scheduled','published']}))

if __name__=='__main__':main()
