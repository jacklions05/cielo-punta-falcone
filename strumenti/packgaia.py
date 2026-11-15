import pathlib
QUI=pathlib.Path(__file__).resolve().parent
PAGINA=(QUI.parent/'index.html').as_uri()
import json, math, gzip, base64, struct, numpy as np
g=np.array(json.load(open(QUI/'dati'/'gaia_tutti.json')),dtype=float)
ref=json.load(open(QUI/'dati'/'starsref.json'))
ra,de,G,T=g.T
# Teff -> B-V (inversione Ballesteros)
bvg=np.linspace(-0.4,2.2,600); Tg=4600*(1/(0.92*bvg+1.7)+1/(0.92*bvg+0.62))
bv=np.where(T>0,np.interp(T,Tg[::-1],bvg[::-1]),np.nan); bv0=np.nan_to_num(bv,nan=0.7)
V=G+0.3*bv0**2
def unit(r,d):
    r=np.radians(r);d=np.radians(d);return np.stack([np.cos(d)*np.cos(r),np.cos(d)*np.sin(r),np.sin(d)],-1)
U=unit(ra,de)
keep=V<=14.4
def kill(r0,d0,rad_as,cond=None):
    u=unit(np.array([r0]),np.array([d0]))[0]; sep=np.degrees(np.arccos(np.clip(U@u,-1,1)))*3600
    m=sep<rad_as
    if cond is not None: m&=cond
    keep[m]=False
nS=0
for s in ref['S']:
    r0,d0,m0=s[0],s[1],s[2]
    if abs(d0)>91: continue
    kill(r0,d0,30,np.abs(V-m0)<1.5)
for r0,d0,sp in ref["D"]: kill(r0,d0,sp+4)
for r0,d0 in ref['SM']: kill(r0,d0,4)
print('tenute',keep.sum(),'di',len(V))
ra,de,V,bv=ra[keep],de[keep],V[keep],bv[keep]
o=np.argsort(de); ra,de,V,bv=ra[o],de[o],V[o],bv[o]
buf=bytearray()
for a,d,m,b in zip(ra,de,V,bv):
    ia=int(round(a*3600))%1296000; id_=int(round((d+90)*3600)); im=max(0,min(255,int(round((m+1)*10)))); ib=255 if b!=b else max(0,min(254,int(round((b+0.5)*80))))
    buf+=struct.pack('<I',ia|(im<<24))[:4]; buf+=struct.pack('<I',id_|(ib<<24))
z=gzip.compress(bytes(buf),9); s=base64.b64encode(z).decode()
print(len(buf),len(z),len(s))
open(QUI/'dati'/'gaia_b64.txt','w').write(s)
