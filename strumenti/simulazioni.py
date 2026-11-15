import pathlib
QUI=pathlib.Path(__file__).resolve().parent
PAGINA=(QUI.parent/'index.html').as_uri()
from playwright.sync_api import sync_playwright
import json,base64
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':900,'height':900})
    pg.goto(PAGINA); pg.wait_for_timeout(4000)
    pg.evaluate("cieloOcu=()=>[20.15,-30];OCU.seeing=false;eval(\"window.disegnaOculare=\"+disegnaOculare.toString().replace(\"alt<0?\",\"false?\").replace(\"sa>-6?\",\"false?\"));window.oggettoOcu=eval('('+oggettoOcu.toString().split('const alt0=altaz(mve(toE(rd[0],rd[1])))[1]').join('const alt0=60')+')');0")
    lst=pg.evaluate("OGGETTI.filter(o=>!['evento','paesaggio','sole','cometa','asteroide'].includes(o.kind)).map(o=>[o.id,o.nome,o.alias||'',o.kind])")
    pg.evaluate('caricaLuna()'); pg.wait_for_timeout(2500)
    out=[]
    for id,nome,alias,kind in lst:
        r=pg.evaluate(f"""(()=>{{const o=OGGETTI.find(x=>x.id==={json.dumps(id)});const D=OCU_DATI[o.id]||[];OCU.ep=(D[1]||0)>25?0:(D[5]==='PN'&&(D[1]||1)<1.5)?4:2;if(o.kind==='luna'){{OCU.ep=0;setFromT(Date.parse('2026-11-18T19:00:00Z'));draw()}}
          if(o.kind==='pianeta')OCU.ep=4;if(GRUPPI[o.id])OCU.ep=0;if(o.kind==='cometa'||o.kind==='asteroide'){{setFromT(Date.parse(o.foto[0].data+'T21:00:00Z'));draw()}}apriOculare(vecOf(o),o.id);const t=[...$('ocuInfo').querySelectorAll('b')].findIndex(b=>b.textContent===o.nome);
          const righe=$('ocuInfo').innerHTML.split('<br>');const riga=righe.find(x=>x.startsWith('<b>'+o.nome+'</b>'))||righe[0]||'';
          return [$('ocuCv').toDataURL('image/jpeg',.8),riga.replace(/<[^>]+>/g,''),OCULARI[OCU.ep][0]+' mm '+OCULARI[OCU.ep][1]+'°']}})()""")
        open(f'cs/{id}.jpg','wb').write(base64.b64decode(r[0].split(',')[1]))
        out.append([id,nome,alias,kind,r[1],r[2]])
    json.dump(out,open('cs/list.json','w'),ensure_ascii=False); print(len(out))
