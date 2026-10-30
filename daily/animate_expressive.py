import numpy as np
from PIL import Image

def align(im,ref):
    # Translation registration on stable facial areas, excluding mouth and eyes.
    a=np.asarray(im.convert('RGB'),dtype=np.float32)
    b=np.asarray(ref.convert('RGB'),dtype=np.float32)
    weights=np.zeros((380,380),bool)
    weights[18:60,100:285]=True
    weights[145:185,140:235]=True
    weights[95:155,175:202]=True
    best=(float('inf'),0,0)
    for dy in range(-14,15):
        for dx in range(-10,11):
            score=float(np.mean(np.abs(np.roll(a,(dy,dx),(0,1))[weights]-b[weights])))
            if score<best[0]:best=(score,dx,dy)
    shifted=Image.new('RGB',im.size)
    shifted.paste(im,(best[1],best[2]))
    return shifted,list(best)
