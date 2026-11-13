import sys, json, numpy as np, cv2, potrace
from PIL import Image

def to_d(curves, ox, oy, s):
    out=[]
    f=lambda p:f"{(p.x+ox)*s:.2f} {(p.y+oy)*s:.2f}"
    for c in curves:
        out.append("M"+f(c.start_point))
        for seg in c.segments:
            if seg.is_corner: out.append("L"+f(seg.c)+"L"+f(seg.end_point))
            else: out.append("C"+f(seg.c1)+" "+f(seg.c2)+" "+f(seg.end_point))
        out.append("Z")
    return "".join(out)

def trace(path, crop, scale, thr=170, minarea=200):
    I=Image.open(path).convert("RGBA"); bg=Image.new("RGBA",I.size,(255,255,255,255)); bg.alpha_composite(I); im=np.array(bg.convert("L"))
    x0,y0,x1,y1=crop; im=im[y0:y1,x0:x1]
    im=cv2.resize(im,None,fx=2,fy=2,interpolation=cv2.INTER_CUBIC)
    mask=(im<thr).astype(np.uint8)
    n,lab,stats,cent=cv2.connectedComponentsWithStats(mask,8)
    comps=[]
    for i in range(1,n):
        x,y,w,h,a=stats[i]
        if a<minarea: continue
        bm=(lab==i)
        curves=potrace.Bitmap(~bm).trace(turdsize=10,alphamax=1.0,opticurve=True,opttolerance=0.2)
        comps.append(dict(x=int(x),d=to_d(curves,0,0,scale/2),bbox=[x*scale/2,y*scale/2,w*scale/2,h*scale/2]))
    comps.sort(key=lambda c:c['x'])
    return dict(w=(x1-x0)*scale,h=(y1-y0)*scale,comps=comps)

U="/root/.claude/uploads/84e8c024-c985-513a-996a-c8d9ffa071c1/"
sym=trace(U+"ad666c83-image.jpg",(400,345,900,965),1.0)
wm=trace(U+"21e4d79c-image.png",(200,1000,3620,1660),0.3,minarea=500)
json.dump(dict(sym=sym,wm=wm),open(sys.argv[1],"w"))
print(len(sym['comps']),[c['bbox'] for c in sym['comps']]); print(len(wm['comps']),[[round(v) for v in c['bbox']] for c in wm['comps']])

# interior holes of symbol (white regions) for sand clipping
I=Image.open(U+"ad666c83-image.jpg").convert("L"); im=np.array(I)[345:965,400:900]
im=cv2.resize(im,None,fx=2,fy=2,interpolation=cv2.INTER_CUBIC)
white=(im>=170).astype(np.uint8)
n,lab,stats,_=cv2.connectedComponentsWithStats(white,4)
holes=[]
for i in range(1,n):
    x,y,w,h,a=stats[i]
    if a<2000 or x==0 or y==0: continue
    curves=potrace.Bitmap(lab!=i).trace(turdsize=10,alphamax=1.0,opticurve=True,opttolerance=0.2)
    holes.append(dict(bbox=[x/2,y/2,w/2,h/2],d=to_d(curves,0,0,.5)))
D=json.load(open(sys.argv[1])); D['holes']=holes; json.dump(D,open(sys.argv[1],'w'))
for h in holes: print([round(v) for v in h['bbox']])
