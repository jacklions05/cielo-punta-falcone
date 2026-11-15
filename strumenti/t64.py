import pathlib
QUI=pathlib.Path(__file__).resolve().parent
PAGINA=(QUI.parent/'index.html').as_uri()
from playwright.sync_api import sync_playwright
import sys
ids=sys.argv[1].split(',')
with sync_playwright() as p:
    b=p.chromium.launch(); errs=[]
    pg=b.new_page(viewport={'width':1000,'height':900}); pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(PAGINA); pg.wait_for_timeout(3500); pg.evaluate('OCU.seeing=false;cieloOcu=()=>[20.15,-30]')
    for id in ids:
        ep=1
        if ':' in id: id,ep=id.split(':'); ep=int(ep)
        r=pg.evaluate(f"""(()=>{{const o=OGGETTI.find(x=>x.id==='{id}');if(!o)return 'manca';const a=altaz(vecOf(o));OCU.ep={ep};apriOculare(vecOf(o),o.id);return [Math.round(a[1]),$('ocuInfo').innerText]}})()""")
        print(id,r); pg.locator('#ocuCv').screenshot(path=fstr(QUI/'o_{id}.png')); pg.evaluate("$('ocu').hidden=true")
    print(errs)
