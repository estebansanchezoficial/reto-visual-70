"""One technical draft, never a scheduled or published TikTok post."""
import hashlib, json, subprocess, urllib.request
from pathlib import Path
import buffer_api as buffer
import cloud
from publish import payload,verify_post

TAG='rv70-publish-transport-test-2026-11-01'


def main():
    buffer.preflight()
    if cloud.api(f'repos/{cloud.REPO}')['private']:raise ValueError('Public standard runner only')
    existing=cloud.api(f'repos/{cloud.REPO}/releases?per_page=100')
    if any(r['tag_name']==TAG for r in existing):raise ValueError('Technical test reserved already; do not repeat')
    out=cloud.ROOT/'output/buffer-smoke';out.mkdir(parents=True)
    video=out/'transport.mp4'
    subprocess.run(['ffmpeg','-v','error','-n','-f','lavfi','-i','color=c=0x123568:s=360x640:r=30:d=4',
                    '-i',str(cloud.ROOT/'assets/music/cipher.mp3'),'-vf',"drawtext=text='PRUEBA TECNICA - NO PUBLICAR':fontsize=17:fontcolor=white:x=(w-tw)/2:y=(h-th)/2",
                    '-af','volume=-24dB','-t','4','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac','-movflags','+faststart',str(video)],check=True)
    sha=hashlib.sha256(video.read_bytes()).hexdigest()
    cloud.gh('release','create',TAG,str(video),'-R',cloud.REPO,'--target','main','--latest=false',
             '--title','Technical transport fixture — NOT a TikTok publication','--notes',json.dumps({'status':'TECHNICAL_TEST_RESERVED','sha256':sha,'scheduled':False,'published':False}))
    url=f'https://github.com/{cloud.REPO}/releases/download/{TAG}/transport.mp4'
    with urllib.request.urlopen(url,timeout=40) as response:download=response.read(1_000_000)
    if hashlib.sha256(download).hexdigest()!=sha:raise ValueError('Transport fixture hash mismatch')
    music=json.loads((cloud.ROOT/'assets/music/license.json').read_text(encoding='utf-8'))
    request=payload('PRUEBA TECNICA. NO PUBLICAR. Solo comprobación de transporte.\n'+music['attribution'],url,None,draft=True)
    request['assets'][0]['video']['metadata']['thumbnailOffset']=0
    created=buffer.create_post(request)
    record={'status':'BUFFER_DRAFT_CREATED','buffer_post_id':created['id'],'scheduled':False,'published':False,'sha256':sha}
    cloud.gh('release','edit',TAG,'-R',cloud.REPO,'--notes',json.dumps(record))
    post=verify_post(buffer.read_post(created['id']),request,draft=True)
    record.update(status='BUFFER_DRAFT_TRANSPORT_VERIFIED',buffer_status=post['status'],ai_label=post['metadata']['isAiGenerated'],asset_sources=[a['source'] for a in post['assets']])
    cloud.gh('release','edit',TAG,'-R',cloud.REPO,'--notes',json.dumps(record))
    print(json.dumps(record))


if __name__=='__main__':main()
