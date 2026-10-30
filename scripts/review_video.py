"""Extract actual encoded frames and compare them to intended timeline frames."""
from io import BytesIO
import json
from pathlib import Path
import subprocess
import sys

from PIL import Image, ImageChops, ImageDraw, ImageStat
import pilot

path=Path(sys.argv[1]).resolve()
stamps=[1,5,9.5,13,20,25,29.5,35,41,47,51.5,57,63,67]
sheet=Image.new('RGB',(1350,1530),'#0b0b15'); draw=ImageDraw.Draw(sheet)
results=[]
for index,t in enumerate(stamps):
    encoded=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(path),'-frames:v','1','-f','image2pipe','-vcodec','png','pipe:1'],timeout=30)
    actual=Image.open(BytesIO(encoded)).convert('RGB')
    error=sum(ImageStat.Stat(ImageChops.difference(actual,pilot.frame(t))).mean)/3
    assert error<5, (t,error)
    results.append({'seconds':t,'scene':pilot.state(t)[1],'mean_absolute_rgb_error':round(error,4)})
    x=index%5*270; y=index//5*510
    sheet.paste(actual.resize((270,480),Image.Resampling.LANCZOS),(x,y))
    draw.text((x+12,y+483),f'{t:g} s / {pilot.state(t)[1]}',font=pilot.font(19),fill=pilot.WHITE)
sheet.save(path.parent/'revision-video.jpg',quality=94)
(path.parent/'revision-video.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'frames_checked':len(results),'maximum_mean_error':max(x['mean_absolute_rgb_error'] for x in results),'status':'PASS'}))
