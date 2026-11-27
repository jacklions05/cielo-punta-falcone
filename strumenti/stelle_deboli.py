"""Stelle da mag 5,3 a 7,0 (d3-celestial stars.8.json, Hipparcos) impacchettate per DEBOLI_B64.
6 byte a stella: AR uint16, Dec uint16, (mag-5)*100 uint8, B-V*60+128 uint8. Uso: python stelle_deboli.py stars.8.json"""
import json,sys,struct,base64
d=json.load(open(sys.argv[1]))
out=bytearray();n=0
for f in d['features']:
    m=f['properties']['mag']
    if not (5.3<m<=7.0):continue
    ra,de=f['geometry']['coordinates'];ra%=360
    if de<-50:continue
    try:bv=float(f['properties']['bv'])
    except:bv=.6
    out+=struct.pack('<HHBB',round(ra/360*65535)%65536,round((de+90)/180*65535),min(255,round((m-5)*100)),max(0,min(255,round(bv*60+128))))
    n+=1
print(n,file=sys.stderr);print(base64.b64encode(bytes(out)).decode())
