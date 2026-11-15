import pathlib
QUI=pathlib.Path(__file__).resolve().parent
PAGINA=(QUI.parent/'index.html').as_uri()
import csv,json,re,math
rows={};byM={}
for fn in ['NGC.csv','addendum.csv']:
    for r in csv.DictReader(open(fn),delimiter=';'):
        rows[r['Name']]=r
        if r['M'] and r['Type']!='Dup': byM.setdefault(int(r['M']),r)
def deg(r):
    h,m,s=map(float,r['RA'].split(':')); ra=15*(h+m/60+s/3600)
    d=r['Dec']; sg=-1 if d[0]=='-' else 1; a,b,c=map(float,d[1:].split(':')); return ra,sg*(a+b/60+c/3600)
def fl(x):
    try: return float(x)
    except: return None
O=json.load(open('ogg2.json'))
out={};miss=[]
for id,nome,kind,tipo,sig,ra,de in O:
    if kind!='dso': continue
    r=None
    for g in (sig or [])+[nome]:
        m=re.match(r'^M\s?(\d+)$',g)
        if m and int(m.group(1)) in byM: r=byM[int(m.group(1))];break
        m=re.match(r'^(NGC|IC)\s?(\d+)$',g)
        if m:
            k=f'{m.group(1)}{int(m.group(2)):04d}'
            if k in rows: r=rows[k]; 
            if r and r['Type']=='Dup' and r['NGC']:
                k2='NGC'+r['NGC'].zfill(4) if not r['NGC'].startswith('IC') else r['NGC']; r=rows.get(k2,r)
            if r: break
    if not r: miss.append((id,nome,tipo)); continue
    mag=fl(r['V-Mag']) or fl(r['B-Mag']); a=fl(r['MajAx']); b=fl(r['MinAx']); pa=fl(r['PosAng']); sb=fl(r['SurfBr'])
    out[id]=[round(mag,1) if mag else None,a,b or a,pa,sb,r['Type'],r['Hubble'] or None]
print(len(out)); print(miss)
json.dump(out,open('ocu.json','w'))
for k in ['M31','M42','M13','M57','M51','N6946','M27','IC434','N7000']:
    print(k,out.get(k))
