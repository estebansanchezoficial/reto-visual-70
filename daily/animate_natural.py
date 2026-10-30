"""Continuous optical-flow facial morphing; approximate lip activity, not forced alignment."""
from pathlib import Path
import subprocess,json,math,hashlib,time
import cv2
import numpy as np
from PIL import Image,ImageDraw,ImageFilter


ROOT=Path(__file__).resolve().parent.parent
OLD=ROOT/'reto-visual-70/output/avatar-alex-expresivo-v2'
OUT=ROOT/'reto-visual-70/output/avatar-alex-natural-v3'
W,H,FPS,N=720,1280,30,450
cv2.setNumThreads(2)

class Morph:
    def __init__(self,a,b):
        self.a=np.asarray(a.convert('RGB'));self.b=np.asarray(b.convert('RGB'))
        ga=cv2.cvtColor(self.a,cv2.COLOR_RGB2GRAY);gb=cv2.cvtColor(self.b,cv2.COLOR_RGB2GRAY)
        opts=(.5,4,25,5,7,1.5,0)
        self.f=cv2.calcOpticalFlowFarneback(ga,gb,None,*opts)
        self.r=cv2.calcOpticalFlowFarneback(gb,ga,None,*opts)
        self.f=cv2.GaussianBlur(self.f,(5,5),0);self.r=cv2.GaussianBlur(self.r,(5,5),0)
        self.x,self.y=np.meshgrid(np.arange(self.a.shape[1],dtype=np.float32),np.arange(self.a.shape[0],dtype=np.float32))
    def at(self,t):
        t=float(np.clip(t,0,1))
        if t<.0001:return Image.fromarray(self.a)
        if t>.9999:return Image.fromarray(self.b)
        wa=cv2.remap(self.a,self.x-self.f[:,:,0]*t,self.y-self.f[:,:,1]*t,cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT)
        wb=cv2.remap(self.b,self.x-self.r[:,:,0]*(1-t),self.y-self.r[:,:,1]*(1-t),cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT)
        return Image.fromarray(cv2.addWeighted(wa,1-t,wb,t,0))

def feather(size):
    m=Image.new('L',size);d=ImageDraw.Draw(m)
    d.rounded_rectangle((8,8,size[0]-8,size[1]-8),radius=24,fill=255)
    return m.filter(ImageFilter.GaussianBlur(5))

def cells(path):
    im=Image.open(path).convert('RGB');s=im.width//2
    return [im.crop(((i%2)*s,(i//2)*s,(i%2+1)*s,(i//2+1)*s)).resize((380,380),Image.Resampling.LANCZOS) for i in range(4)]

def pulse(t,center):
    # Eyelid closes quickly, then opens gradually; continuous between samples.
    x=t-center
    if -.07<x<0:return .5-.5*math.cos(math.pi*(x+.07)/.07)
    if 0<=x<.035:return 1.
    if .035<=x<.175:return .5+.5*math.cos(math.pi*(x-.035)/.14)
    return 0.

def controls(wave,sentences):
    energy=[]
    for i in range(N):
        center=round((i/FPS+.018)*24000)
        part=wave[max(0,center-600):center+600]
        energy.append(float(np.sqrt(np.mean(part**2))) if len(part) else 0.)
    q=float(np.percentile([e for e in energy if e>.015],90))
    # Vowel order gives a weak rounding cue within each known sentence duration.
    # This is estimated timing, explicitly not a phonetic aligner.
    cues=[]
    vowels=set('aeiouɛɔɪʊ')
    for sent in sentences:
        units=[c for c in sent['phonemes'] if c.isalpha() or c==' ']
        weights=[1.65 if c in vowels else (.28 if c==' ' else .72) for c in units]
        total=sum(weights);cursor=0
        for c,weight in zip(units,weights):
            if c in vowels:cues.append((sent['start']+sent['duration']*(cursor+weight/2)/total,1. if c in 'ouɔʊ' else 0.))
            cursor+=weight
    times=np.array([a for a,b in cues]);values=np.array([b for a,b in cues])
    rows=[];jaw=0.;rounded=0.
    for i,e in enumerate(energy):
        t=i/FPS
        talking=any(s['start']-.025<=t<=s['start']+s['duration']+.025 for s in sentences)
        target=(float(np.clip((e-.025)/(q-.025),0,1))**.72)*.82 if talking else 0.
        tau=.050 if target>jaw else .085
        candidate=jaw+(target-jaw)*(1-math.exp(-1/FPS/tau))
        jaw+=float(np.clip(candidate-jaw,-.14,.14))
        rtarget=float(np.interp(t,times,values))*.7 if talking else 0.
        rounded+=(rtarget-rounded)*(1-math.exp(-1/FPS/.105))
        blink=max(pulse(t,c) for c in [1.27,4.34,8.36,12.4])
        brow=sum(.23*math.exp(-.5*((t-c)/.35)**2) for c in [2.8,9.7])
        rows.append({'frame':i,'t':round(t,4),'jaw':round(jaw,5),'rounding':round(rounded,5),'blink':round(blink,5),'brow':round(brow,5),'rms':round(e,5)})
    return rows
