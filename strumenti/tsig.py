import pathlib
QUI=pathlib.Path(__file__).resolve().parent
PAGINA=(QUI.parent/'index.html').as_uri()
from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page()
    pg.goto(PAGINA); pg.wait_for_timeout(2000)
    r=pg.evaluate("OGGETTI.filter(o=>o.kind==='dso').map(o=>[o.id,o.nome,o.alias||'',(o._sigle||[]).join('|')])")
    json.dump(r,open('sigle.json','w'),ensure_ascii=False); print(len(r)); print(r[:5]); print(pg.evaluate("DAFARE.slice(-3)"))
