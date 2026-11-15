# Uso: python estrai_gaia.py [campi.json]  (gira sul PC con Siril e il catalogo Gaia locale installato)
# Estrae stelle Gaia DR3 dal catalogo locale di Siril attorno a una lista di campi.
import struct, math, json, os, sys
CAT=os.path.join(os.environ['LOCALAPPDATA'],'siril','siril_cat_healpix8_astro.dat')
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'gaia_campi.json')
NSIDE=256; R=0.5; GMAX=14.8
T=json.load(open(sys.argv[1])) if len(sys.argv)>1 else json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'dati','tl.json')))  # elenco [ra,dec] dei centri dei campi
jrll=[2,2,2,2,3,3,3,3,4,4,4,4]; jpll=[1,3,5,7,0,2,4,6,1,3,5,7]
def spread(v):
    r=0
    for b in range(16):
        if v>>b&1: r|=1<<(2*b)
    return r
def ang2pix(ra,de):
    z=math.sin(math.radians(de)); phi=math.radians(ra)%(2*math.pi)
    za=abs(z); tt=phi/(math.pi/2)
    if za<=2/3:
        temp1=NSIDE*(0.5+tt); temp2=NSIDE*z*0.75
        jp=int(temp1-temp2); jm=int(temp1+temp2)
        ifp=jp//NSIDE; ifm=jm//NSIDE
        face=(ifp|4) if ifp==ifm else (ifp if ifp<ifm else ifm+8)
        ix=jm&(NSIDE-1); iy=NSIDE-(jp&(NSIDE-1))-1
    else:
        ntt=min(int(tt),3); tp=tt-ntt
        tmp=NSIDE*math.sqrt(3*(1-za))
        jp=min(int(tp*tmp),NSIDE-1); jm=min(int((1-tp)*tmp),NSIDE-1)
        if z>=0: face=ntt; ix=NSIDE-jm-1; iy=NSIDE-jp-1
        else: face=ntt+8; ix=jp; iy=jm
    return face*NSIDE*NSIDE+spread(ix)+(spread(iy)<<1)
f=open(CAT,'rb'); hdr=f.read(128)
print(hdr[:48].rstrip(b'\0').decode(), 'livello',hdr[49],'tipo',hdr[50],'chunk',hdr[51])
NP=12*NSIDE*NSIDE; idx=struct.unpack('<%dI'%NP,f.read(NP*4)); D0=128+NP*4
K=360/(2**31-1); stelle={}; campi=[]
for n,(ra,de) in enumerate(T):
    pix=set(); st=4/60; cd=max(math.cos(math.radians(de)),0.05)
    k=int(R/st)+2
    for i in range(-k,k+1):
        for j in range(-k,k+1):
            d2=de+j*st
            if abs(d2)>90: continue
            pix.add(ang2pix(ra+i*st/cd,d2))
    ids=[]
    for p in sorted(pix):
        a=idx[p-1] if p>0 else 0; b=idx[p]
        if b<=a: continue
        f.seek(D0+a*16); buf=f.read((b-a)*16)
        for r in struct.iter_unpack('<iihhHh',buf):
            g=r[5]/1000
            if g>GMAX: continue
            sra=r[0]*K; sde=r[1]*K
            if sra<0: sra+=360
            dd=math.degrees(math.acos(max(-1,min(1,math.sin(math.radians(de))*math.sin(math.radians(sde))+math.cos(math.radians(de))*math.cos(math.radians(sde))*math.cos(math.radians(sra-ra))))))
            if dd>R: continue
            key=(r[0],r[1])
            if key not in stelle: stelle[key]=[round(sra,5),round(sde,5),round(g,2),r[4]]
    if n%20==0: print(n,len(T),len(stelle)); sys.stdout.flush()
json.dump(list(stelle.values()),open(OUT,'w'),separators=(',',':'))
print('FATTO',len(stelle),'stelle ->',OUT)
