import pathlib
QUI=pathlib.Path(__file__).resolve().parent
PAGINA=(QUI.parent/'index.html').as_uri()
from playwright.sync_api import sync_playwright
import sys
URL='http://localhost:8765/index.html'
def run(vp,tag):
    with sync_playwright() as p:
        br=p.chromium.launch(); errs=[]; pg=br.new_page(viewport=vp)
        pg.on('pageerror',lambda e:errs.append('PAGEERR '+str(e)+' | '+str(getattr(e,'stack',''))[:600]))
        pg.on('console',lambda m:errs.append('CONSOLE '+m.text) if m.type=='error' else None)
        pg.goto(URL); pg.wait_for_timeout(4000)
        note=[]
        def ev(js,label=None):
            try: return pg.evaluate(js)
            except Exception as e: errs.append(f'EVAL {label or js[:60]}: {e}'); return None
        def clk(sel):
            try: pg.locator(sel).first.click(timeout=3000)
            except Exception as e: errs.append(f'CLICK {sel}: {str(e)[:120]}')
        if vp['width']<700: clk('#bMenu')
        for b in ['#bList','#bElba','#bAll','#bLay','#bLay','#bEcl','#bEcl','#bRed','#bRed']:
            clk(b); pg.wait_for_timeout(250)
        # lista e selezione
        ev("$('cerca').value='M31';$('cerca').dispatchEvent(new Event('input'))"); pg.wait_for_timeout(400)
        ev("select('M31')"); pg.wait_for_timeout(500)
        note.append(('pannello M31', ev("!$('panel').hidden && $('panel').innerText.slice(0,40)")))
        ev("select('M42')"); pg.wait_for_timeout(400)
        note.append(('scroll pannello', ev("$('panel').scrollTop")))
        # tutti gli oggetti: pannello e oculare senza errori
        n=ev("""(()=>{let k=0;for(const o of OGGETTI){try{select(o.id);if(o.ra!=null||o.kind==='luna'||o.kind==='pianeta'){OCU.ep=1;apriOculare(vecOf(o),o.id);$('ocu').hidden=true}k++}catch(e){console.error('OGG '+o.id+' '+e.message)}}return k})()""")
        note.append(('oggetti provati',n))
        # soci e stanotte
        ev("$('cerca').value='soci';$('cerca').dispatchEvent(new Event('input'))"); pg.wait_for_timeout(500)
        note.append(('soci', ev("$('listUl').children.length")))
        ev("$('cerca').value='';$('cerca').dispatchEvent(new Event('input'))")
        clk('#bNotte'); pg.wait_for_timeout(800); note.append(('stanotte', ev("$('listUl').children.length"))); clk('#bNotte')
        # tempo
        clk('#bTempo'); pg.wait_for_timeout(200); clk('#bStory'); pg.wait_for_timeout(2500); clk('#bStory'); clk('#bNow'); pg.wait_for_timeout(300)
        # cupola
        clk('#bCupola'); pg.wait_for_timeout(1200)
        ev("select('M13')"); pg.wait_for_timeout(9000)
        for b in ['#tVel','#tVel','#tVel','#tIns','#tIns','#tCen']: clk(b); pg.wait_for_timeout(200)
        clk('#bOcu'); pg.wait_for_timeout(500)
        note.append(('oculare aperto', ev("$('ocuInfo').innerText.slice(0,80)")))
        for i in range(3): ev(f"document.querySelectorAll('#ocuEp button')[{i}].click()"); pg.wait_for_timeout(200)
        clk('#ocuSee'); clk('#ocuSee')
        pg.keyboard.press('ArrowUp'); pg.wait_for_timeout(300); pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
        clk('#bPort'); pg.wait_for_timeout(5000)
        clk('#bOcu'); pg.wait_for_timeout(500)
        note.append(('cupola chiusa', ev("$('ocuInfo').innerText.slice(0,80)")))
        pg.keyboard.press('Escape'); clk('#bPort'); pg.wait_for_timeout(5000); clk('#bOcu'); pg.wait_for_timeout(400)
        note.append(('riaperta', ev("$('ocuInfo').innerText.slice(0,60)"))); pg.keyboard.press('Escape')
        clk('#bSct'); pg.wait_for_timeout(1500); clk('#sctLiv button:nth-child(2)'); pg.wait_for_timeout(800); pg.keyboard.press('Escape')
        note.append(('sct chiuso', ev("$('sct').hidden")))
        clk('#tPark'); pg.wait_for_timeout(6000)
        clk('#bCupola'); pg.wait_for_timeout(800)
        clk('#bSuoni'); pg.wait_for_timeout(500); clk('#bSuoni')
        pg.screenshot(path=f'smoke_{tag}.png')
        br.close()
        return errs,note
for vp,tag in [({'width':1300,'height':850},'pc')]:
    e,n=run(vp,tag); print('==',tag); [print(' ',x) for x in n]; print(' errori:',len(e)); [print('  ',x[:900]) for x in e[:25]]
