"""Mix licensed music into an already verified voice-only package; never publish."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def checked_license():
    data = json.loads((ROOT / 'assets/music/license.json').read_text(encoding='utf-8'))
    track = ROOT / 'assets/music' / data['file']
    if data['license'] != 'CC BY 4.0' or digest(track) != data['sha256']:
        raise ValueError('Music license/file mismatch')
    return data, track


def pause_windows(sentences, duration):
    """Protect speech plus a margin; raise only in gaps at least one second long."""
    protected = sorted((max(0., s['start']-.2), min(duration, s['start']+s['duration']+.25)) for s in sentences)
    cursor = 0.
    gaps = []
    for start, end in protected + [(duration, duration)]:
        if start-cursor >= 1.:
            gaps.append((round(cursor, 5), round(start, 5)))
        cursor = max(cursor, end)
    return gaps


def volume_expression(data, gaps):
    voice = 10**(data['volume_db']/20)
    pause = 10**(data.get('pause_volume_db', data['volume_db'])/20)
    transition = data.get('transition_seconds', .35)
    ramps = [f'max(0,min(1,min((t-{a})/{transition},({b}-t)/{transition})))' for a,b in gaps]
    return f"{voice:.9f}+{pause-voice:.9f}*({'+'.join(ramps) or '0'})"


def mix(folder):
    import numpy as np
    folder = Path(folder)
    data, track = checked_license()
    source = folder / 'video.mp4'
    qa_path = folder / 'verificacion-final.json'
    qa = json.loads(qa_path.read_text(encoding='utf-8'))
    if qa.get('music_embedded') or (folder / 'video-sin-musica.mp4').exists():
        raise ValueError('Music already applied or incomplete previous attempt; reconcile first')
    if qa['status'] != 'PASS_PENDING_USER_APPROVAL' or digest(source) != qa['sha256']:
        raise ValueError('Source video has not passed verification or changed')
    target = folder / 'video-con-musica.mp4'
    duration = float(qa['duration'])
    narration = json.loads((folder/'narracion.json').read_text(encoding='utf-8'))
    gaps = pause_windows(narration['sentences'], duration)
    envelope = volume_expression(data, gaps)
    filt = (f"[1:a]atrim=duration={duration},asetpts=PTS-STARTPTS,"
            f"volume='{envelope}':eval=frame,afade=t=in:st=0:d=1,"
            f"afade=t=out:st={duration-2}:d=2[m];"
            "[0:a][m]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
            "alimiter=limit=0.95:level=false:latency=true[a]")
    subprocess.run(['ffmpeg', '-v', 'error', '-n', '-i', str(source), '-i', str(track),
                    '-filter_complex', filt, '-map', '0:v:0', '-map', '[a]', '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '192k', '-t', str(duration), '-movflags', '+faststart',
                    str(target)], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-i', str(target), '-f', 'null', '-'], check=True)
    probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_format',
                                               '-show_streams', '-of', 'json', str(target)]))
    v = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    a = next(s for s in probe['streams'] if s['codec_type'] == 'audio')
    if abs(float(probe['format']['duration']) - duration) > .05 or a['codec_name'] != 'aac':
        raise ValueError('Mixed duration/codec failed')
    if (v['width'], v['height'], v['avg_frame_rate']) != (1080, 1920, '30/1'):
        raise ValueError('Mixed video format failed')
    # Compare decoded frame checksums: copied video must preserve every image.
    def frames(path):
        return subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(path),
                                        '-map', '0:v:0', '-f', 'framemd5', '-'])
    if frames(source) != frames(target):
        raise ValueError('Mixed video frames changed')
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(target), '-vn',
                                   '-f', 'f32le', '-ac', '1', '-ar', '24000', 'pipe:1'])
    sound = np.frombuffer(raw, dtype='<f4')
    peak = float(np.max(np.abs(sound)))
    if not peak < 1:
        raise ValueError('Mixed audio clips')
    for speech in qa['narrated_segments']:
        start, end = speech['start'] + .08, speech['start'] + speech['duration'] - .08
        rms = float(np.sqrt(np.mean(sound[round(start*24000):round(end*24000)]**2)))
        if rms < .015:
            raise ValueError('Narrated segment missing from mixed audio')
    (folder / 'verificacion-sin-musica.json').write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding='utf-8')
    source.rename(folder / 'video-sin-musica.mp4')
    target.rename(source)
    qa.update(source_voice_only_sha256=qa['sha256'], sha256=digest(source), bytes=source.stat().st_size,
              music_embedded=True, music=data, audio_peak=peak, decoded_video_frames_unchanged=True,
              music_pause_windows=gaps, music_volume_expression=envelope,
              scheduled=False, published=False)
    qa['voice_only_silence_checks'] = qa.pop('silence_checks', [])
    qa['limits'] += ' Music mixed after voice-only QA; final subjective balance requires new approval.'
    qa_path.write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding='utf-8')
    caption = folder / 'descripcion.txt'
    caption.write_text(caption.read_text(encoding='utf-8').strip() + '\n\n' + data['attribution'] + '\n', encoding='utf-8')
    plan_path = folder / 'plan.json'
    plan = json.loads(plan_path.read_text(encoding='utf-8'))
    plan.update(music=data, music_embedded=True, scheduled=False, published=False)
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding='utf-8')
    for name in ['manifest.json', 'comparison.json']:
        path = folder / name
        record = json.loads(path.read_text(encoding='utf-8'))
        if name == 'comparison.json':
            record['video_sha256'] = qa['sha256']
        record.update(music_embedded=True, final_video_sha256=qa['sha256'])
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    (folder / 'music.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    return qa


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('folder')
    args = parser.parse_args()
    print(json.dumps(mix(args.folder), ensure_ascii=False))
