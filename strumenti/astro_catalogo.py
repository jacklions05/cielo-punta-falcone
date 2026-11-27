"""Costruisce astro-dati.js: il catalogo della pagina «Astro» (pianificazione delle riprese).

Ingressi:
  /tmp/cat/dump.json         oggetti della mappa (OGGETTI tipo dso, OCU_DATI, DAFARE), estratti con Playwright da index.html
  dati/NGC.csv, addendum.csv OpenNGC (CC-BY-SA 4.0): magnitudini, assi, luminosità superficiale media (SurfBr, banda B)
  /tmp/cat/harris_mwgc.txt   Harris 1996 (ed. 2010): V totale e raggio di metà luce dei globulari
  /tmp/cat/hcg.yaml          Hickson 1982 (CDS VII/213): posizioni J2000 e diametri dei 100 gruppi compatti
  /tmp/cat/hick.edb          stesso catalogo in formato XEphem: magnitudine B e assi di ogni galassia dei gruppi

Per ogni oggetto calcola la luminosità superficiale media μ (mag/″², banda V) e dice come l'ha ottenuta:
  galassie        SurfBr di OpenNGC − 0,85 (colore B−V tipico); senza SurfBr: m + 2,5·log10(π/4·a·b) sull'ellisse
  globulari       luce entro il raggio di metà luce r_h (Harris): μ_h = V_t + 0,753 + 2,5·log10(π r_h²)
  ammassi aperti  non conta la superficie ma le stelle: si punta alle stelle deboli, m* = V_t + 12 (tra 15 e 19)
  nebulose, PN    m + 2,5·log10(π/4·a·b) (magnitudine e assi curati della mappa, poi OpenNGC)
  gruppi Hickson  mediana delle μ delle galassie del gruppo (B − 0,9 → V)
Uso: python astro_catalogo.py  (scrive ../astro-dati.js)
"""
import csv, json, math, re, os, statistics as st

QUI = os.path.dirname(os.path.abspath(__file__))
D = json.load(open('/tmp/cat/dump.json'))

# ---------------- OpenNGC ----------------
NGC = {}; MESS = {}
for f in ('NGC.csv', 'addendum.csv'):
    for r in csv.DictReader(open(os.path.join(QUI, 'dati', f), encoding='utf-8'), delimiter=';'):
        NGC[r['Name']] = r
        if r.get('M'): MESS.setdefault(int(r['M']), r)
def fnum(x):
    try: return float(x)
    except: return None
def chiave(s):
    s = s.strip()
    m = re.fullmatch(r'M\s*(\d+)', s)
    if m: return ('M', int(m.group(1)))
    m = re.fullmatch(r'(NGC|IC)\s*(\d+)\s*([A-Z]?)', s, re.I)
    if m: return ('N', f"{m.group(1).upper()}{int(m.group(2)):04d}{m.group(3).upper()}")
    return None
def riga(o):
    for s in [o['nome']] + (o.get('sigle') or []):
        k = chiave(s)
        if not k: continue
        if k[0] == 'M' and k[1] in MESS:
            r = MESS[k[1]]
            if r['Type'] == 'Dup' and r.get('NGC'): r = NGC.get('NGC' + r['NGC'].split(',')[0].zfill(4), r)
            return r
        if k[0] == 'N' and k[1] in NGC:
            r = NGC[k[1]]
            if r['Type'] == 'Dup' and r.get('NGC'): r = NGC.get('NGC' + r['NGC'].split(',')[0].zfill(4), r)
            return r
    return None

# ---------------- Harris ----------------
H1, H2, H3 = {}, {}, {}
sez = 0
for l in open('/tmp/cat/harris_mwgc.txt', encoding='latin-1'):
    if l.strip().startswith('ID') and 'Name' in l: sez = 1; continue
    if l.strip().startswith('ID') and '[Fe/H]' in l: sez = 2; continue
    if l.strip().startswith('ID') and 'v_r' in l: sez = 3; continue
    if not l.strip() or l.startswith('_') or sez == 0: continue
    idn = l[:12].strip()
    if sez == 1:
        H1[idn] = l[12:25].strip()
    elif sez == 2:
        v = fnum(l[40:47].strip()) if len(l) > 47 else None
        H2[idn] = v
    elif sez == 3:
        p = l[12:].split()
        nums = [x for x in p if re.fullmatch(r'-?\d+(\.\d+)?', x)]
        # ultime colonne: r_c r_h mu_V rho_0 lg(tc) lg(th) (alcune possono mancare)
        H3[idn] = l
def harris(o):
    for s in [o['nome']] + (o.get('sigle') or []):
        k = chiave(s)
        if not k: continue
        cand = []
        if k[0] == 'N': cand.append(re.sub(r'^(NGC|IC)0*', r'\1 ', k[1]))
        if k[0] == 'M':
            r = MESS.get(k[1]);
            if r and r.get('NGC'): cand.append('NGC ' + str(int(r['NGC'].split(',')[0])))
            cand += [i for i, n in H1.items() if n.replace(' ', '') == f'M{k[1]}']
        for c in cand:
            if c in H3:
                l = H3[c]; vt = H2.get(c)
                # colonne a larghezza fissa: V_t ai caratteri 40-46 della seconda parte, r_h 64-69 e mu_V 70-77 della terza (controllate su NGC 6266 e NGC 7078)
                rh = fnum(l[64:70].strip()); muc = fnum(l[70:78].strip())
                return vt, rh, muc, c
    return None

# ---------------- dati curati della mappa ----------------
OCU = D['OCU']
TIPI = {'G': 'G', 'GPair': 'GGrp', 'GTrpl': 'GGrp', 'GGroup': 'GGrp', 'GCl': 'GCl', 'OCl': 'OCl', '*Ass': 'OCl', 'PN': 'PN', 'HII': 'HII', 'EmN': 'HII', 'Neb': 'Neb',
        'RfN': 'RfN', 'SNR': 'SNR', 'Cl+N': 'ClN', 'DrkN': 'DrkN', '*': 'Ast', '**': 'Ast', 'Other': 'Oth', 'Nova': 'Oth', 'NonEx': 'Oth'}
TIPO_IT = {'Galassia': 'G', 'Galassia spirale': 'G', 'Galassia ellittica': 'G', 'Galassia irregolare': 'G', 'Galassie interagenti': 'GGrp', 'Coppia di galassie': 'GGrp',
           'Gruppo di galassie': 'GGrp', 'Ammasso di galassie': 'GGrp', 'Ammasso globulare': 'GCl', 'Ammasso aperto': 'OCl', 'Nebulosa planetaria': 'PN',
           'Nebulosa a emissione': 'HII', 'Nebulosa': 'Neb', 'Nebulosa a riflessione': 'RfN', 'Resto di supernova': 'SNR', 'Ammasso e nebulosa': 'ClN',
           'Nebulosa e ammasso': 'ClN', 'Nebulosa oscura': 'DrkN', 'Asterismo': 'Ast'}
def mu_ellisse(m, a, b):
    if m is None or not a: return None
    b = b or a
    return m + 2.5 * math.log10(math.pi / 4 * a * b * 3600)

R1 = lambda x: None if x is None else round(x, 2)
out = []
for o in D['O']:
    r = riga(o); c = OCU.get(o['id']) or OCU.get(re.sub(r'[XR]$', '', o['id']))
    t = TIPO_IT.get(o['tipo']) or (TIPI.get(r['Type']) if r else None) or 'Oth'
    m = a = b = None; fonte = []
    if c and c[0] is not None: m, a, b = c[0], c[1], c[2]; fonte.append('mappa')
    if r:
        V, Bm = fnum(r['V-Mag']), fnum(r['B-Mag'])
        if m is None: m = V if V is not None else (Bm - (.8 if t in ('G', 'GGrp') else 0) if Bm is not None else None)
        if not a: a, b = fnum(r['MajAx']), fnum(r['MinAx'])
        fonte.append('OpenNGC')
    mu = ms = None; metodo = ''
    if t == 'G' and r and fnum(r['SurfBr']):
        mu = fnum(r['SurfBr']) - .85; metodo = 'OpenNGC: luminosità superficiale media entro l\'isofota 25 (B), −0,85 per la banda V'
    elif t == 'GCl':
        h = harris(o)
        if h and h[0] is not None and h[1]:
            vt, rh, muc, hid = h
            mu = vt + .753 + 2.5 * math.log10(math.pi * (rh * 60) ** 2); m = m or vt
            metodo = f'Harris ({hid}): metà della luce (V_t {vt:.2f} + 0,75) entro r_h = {rh:.2f}′' + (f'; centro μ_V {muc:.1f}' if muc else '')
            fonte.append('Harris')
    elif t == 'OCl':
        if m is not None:
            ms = min(19, max(15, m + 12)); metodo = f'Ammasso aperto: conta la luce delle stelle; obiettivo le stelle deboli dell\'ammasso, magnitudine {ms:.1f} (V_t + 12, tra 15 e 19)'
    if mu is None and t not in ('OCl', 'DrkN', 'Ast') and m is not None and a:
        mu = mu_ellisse(m, a, b); metodo = 'magnitudine totale distribuita sull\'ellisse degli assi (media)'
    if t == 'ClN' and mu is None and m is not None:
        ms = min(19, max(15, m + 12))
    liste = []
    if not o['dafare']: liste.append('foto')
    if re.fullmatch(r'M \d+', o['nome']): liste.append('messier')
    if o['dafare']:
        g = next((x[7] for x in D['DAF'] if x[0] == o['id']), '')
        if g: liste.append(g)
    out.append({'id': o['id'], 'n': o['nome'], 'al': o.get('alias') or '', 'ra': round(o['ra'], 4), 'de': round(o['dec'], 4), 't': t, 'm': R1(m),
                'A': R1(a), 'B': R1(b or a), 'mu': R1(mu), 'ms': R1(ms), 'met': metodo, 'li': liste, 'fo': o.get('foto', 0)})

# ---------------- Hickson ----------------
gr = {}
cur = None
for l in open('/tmp/cat/hcg.yaml', encoding='utf-8'):
    l = l.rstrip()
    if l.startswith('- '): cur = {}; l = '  ' + l[2:]
    mm = re.match(r'\s+(\w+): "?(.*?)"?$', l)
    if mm and cur is not None:
        cur[mm.group(1)] = mm.group(2)
        if mm.group(1) == 'type': gr[cur['name']] = cur
GAL = {}; CEN = {}
def sex(x):
    v = [float(t) for t in x.replace('-', '').split(':')]
    v = v[0] + (v[1] if len(v) > 1 else 0) / 60 + (v[2] if len(v) > 2 else 0) / 3600
    return -v if x.strip().startswith('-') else v
for l in open('/tmp/cat/hick.edb', encoding='utf-8'):
    if l.startswith('#') or not l.strip(): continue
    p = l.strip().split(',')
    nome = p[0].split('|')[0]
    mm = re.fullmatch(r'HCG (\d+)([a-z])', nome)
    mg = re.fullmatch(r'HCG (\d+)', nome)
    if mg: CEN[int(mg.group(1))] = (sex(p[2]) * 15, sex(p[3])); continue
    if not mm: continue
    mag = fnum(p[4]); ax = p[6].split('|') if len(p) > 6 else []
    A = fnum(ax[0]) if ax else None; Bx = fnum(ax[1]) if len(ax) > 1 else A
    GAL.setdefault(int(mm.group(1)), []).append((mm.group(2), mag, A, Bx, p[0].split('|')[1:], sex(p[2]) * 15, sex(p[3])))
def hms(s, ore):
    x = [float(v) for v in s.split()]; v = abs(x[0]) + x[1] / 60 + x[2] / 3600
    v = -v if s.strip().startswith('-') else v
    return v * 15 if ore else v
# Gli assi di Hickson sono interni (circa metà del diametro D25): confrontando le 78 galassie del catalogo che hanno anche
# la luminosità superficiale di OpenNGC, la μ calcolata con gli assi di Hickson è più brillante di 3,53 mag (mediana).
# La correggo, così i gruppi sono sulla stessa scala delle galassie; per il disegno allungo gli assi di 1,9 (rapporto mediano con OpenNGC).
HCG_CAL, HCG_ASSI = 3.53, 1.9
def off(i, x):
    c = CEN.get(i)
    if not c: return [0, 0]
    return [R1((x[5] - c[0]) * math.cos(math.radians(c[1])) * 60), R1((x[6] - c[1]) * 60)]
for i in range(1, 101):
    g = gr.get(f'HCG {i}')
    if not g: continue
    ra, de = hms(g['ra'], True), hms(g['dec'], False)
    mem = [x for x in GAL.get(i, []) if x[1] is not None and x[2]]
    mus = sorted(x[1] - .9 + 2.5 * math.log10(math.pi / 4 * (x[2] / 60) * (x[3] / 60 or x[2] / 60) * 3600) + HCG_CAL for x in mem)
    tot = -2.5 * math.log10(sum(10 ** (-.4 * (x[1] - .9)) for x in mem)) if mem else None
    alt = [s for x in mem for s in x[4] if re.match(r'N\d', s)]
    al = ', '.join('NGC ' + s[1:] for s in alt[:4])
    out.append({'id': f'HCG{i}', 'n': f'HCG {i}', 'al': al, 'ra': round(ra, 4), 'de': round(de, 4), 't': 'GGrp', 'm': R1(tot), 'A': float(g['size']), 'B': float(g['size']),
                'mu': R1(st.median(mus)) if mus else None, 'ms': None,
                'met': f'Hickson (CDS VII/213): mediana delle μ delle {len(mus)} galassie del gruppo (B − 0,9 → V, riportate sulla scala di OpenNGC: +3,53); la più brillante {mus[0]:.1f}' if mus else 'Hickson: senza fotometria delle galassie',
                'li': ['hcg'], 'fo': 0, 'mem': [[x[0], R1(x[1] - .9), R1(x[2] / 60 * HCG_ASSI), R1((x[3] or x[2]) / 60 * HCG_ASSI)] + off(i, x) for x in sorted(mem, key=lambda x: x[1])]})

senza = [o['n'] for o in out if o['mu'] is None and o['ms'] is None]
print(len(out), 'oggetti;', len(senza), 'senza calcolo:', senza[:40])
js = '/* Catalogo della pagina Astro: generato da strumenti/astro_catalogo.py. Non modificare a mano. */\nconst AST_CAT=' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n'
open(os.path.join(QUI, '..', 'astro-dati.js'), 'w', encoding='utf-8').write(js)
print(len(js), 'byte')
