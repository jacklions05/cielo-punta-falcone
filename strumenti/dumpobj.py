import pathlib
QUI=pathlib.Path(__file__).resolve().parent
PAGINA=(QUI.parent/'index.html').as_uri()
from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page()
    pg.goto(PAGINA); pg.wait_for_timeout(1500)
    r=pg.evaluate("""OGGETTI.filter(o=>typeof o.ra==='number'&&typeof o.dec==='number').map(o=>[o.id,o.ra,o.dec,o.tipo||''])""")
    r2=pg.evaluate("typeof DAFARE!=='undefined'?DAFARE.map(x=>[x[0],x[5],x[6]]):[]")
    print(len(r),len(r2)); json.dump({'o':r,'d':r2},open('targets.json','w'))
    print(r[:5])
