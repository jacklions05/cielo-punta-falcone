import pathlib
QUI=pathlib.Path(__file__).resolve().parent
PAGINA=(QUI.parent/'index.html').as_uri()
import json,io
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
pdfmetrics.registerFont(TTFont('S','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'));pdfmetrics.registerFont(TTFont('SB','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
L=json.load(open('cs/list.json'))
ORD={'dso':0,'pianeta':2,'luna':2,'stella':1,'cometa':3,'asteroide':3}
SEZ=['Oggetti del profondo cielo','Stelle','Luna e pianeti','Comete e asteroidi']
L.sort(key=lambda x:ORD.get(x[3],0))
W,H=A4;M=28;cols,rows=4,4;cw=(W-2*M)/cols;top=H-M-40;ch=(top-M)/rows
c=canvas.Canvas(str(QUI/'oculare-simulazioni.pdf'),pagesize=A4);c.setTitle('Cielo di Punta Falcone · gli oggetti all\'oculare')
def testata(n):
    c.setFillColorRGB(.08,.08,.08);c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColorRGB(.92,.92,.92);c.setFont('SB',13);c.drawString(M,H-M-12,"Cielo di Punta Falcone · come appaiono all'oculare")
    c.setFont('S',7.5);c.setFillColorRGB(.6,.6,.6);c.drawString(M,H-M-25,"Simulazioni disegnate, non foto · Meade 14″ f/8 · cielo SQM 20,15 · cerchio grande quanto il campo apparente · stelle vere (Gaia DR3)")
    c.drawRightString(W-M,H-M-12,f"pag. {n}")
def wrap(t,font,size,w):
    out=[];line=''
    for wd in t.split():
        tt=(line+' '+wd).strip()
        if pdfmetrics.stringWidth(tt,font,size)<=w: line=tt
        else: out.append(line);line=wd
    if line: out.append(line)
    return out
pag=1;k=0;sez=None;testata(pag)
for id,nome,alias,kind,desc,ep in L:
    s=SEZ[ORD.get(kind,0)]
    if k==cols*rows: c.showPage();pag+=1;k=0;testata(pag)
    col,row=k%cols,k//cols;x=M+col*cw;y=top-(row+1)*ch
    im=Image.open(f'cs/{id}.jpg').convert('RGB')
    if kind=='pianeta': w=im.width;z=w//7;im=im.crop((w//2-z,w//2-z,w//2+z,w//2+z));desc=desc+' [dettaglio ingrandito del centro del campo]'
    im=im.resize((300,300),Image.LANCZOS);b=io.BytesIO();im.save(b,'JPEG',quality=62);b.seek(0)
    sz=cw-26;c.drawImage(ImageReader(b),x+13,y+ch-sz-4,sz,sz)
    if s!=sez: sez=s;c.setFillColorRGB(.95,.75,.35);c.setFont('SB',6.5);c.drawString(x+4,y+ch-2,s.upper())
    c.setFillColorRGB(.95,.95,.95);c.setFont('SB',8);ty=y+ch-sz-15
    t=desc.split(': ',1);tit=t[0] if len(t)>1 else nome;d=t[1] if len(t)>1 else desc
    for ln in wrap(tit,'SB',8,cw-8)[:2]: c.drawString(x+4,ty,ln);ty-=9.5
    c.setFillColorRGB(.7,.7,.7);c.setFont('S',6.3)
    for ln in wrap(d+f' (oculare {ep} apparenti)','S',6.3,cw-8)[:8]: c.drawString(x+4,ty,ln);ty-=7.3
    k+=1
c.save()
