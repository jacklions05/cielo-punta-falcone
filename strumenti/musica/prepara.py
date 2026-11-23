"""Dai MIDI di LilyPond (partiture Mutopia) a dati compatti per la pagina, con un'esecuzione "umana":
tempo che respira, rallentando finale, melodia in rilievo, accompagnamento più piano, pedale di risonanza."""
import mido, math, random, base64, json, sys

BRANI = {
  # nome: file, fattore di tempo (>1 = più lento), periodo del pedale in quarti, tracce da tenere, inizio della battuta (quarti)
  'gym':   dict(f='ly/gym.midi',    lento=60/66, ped=3.0, ok=None),
  'clair': dict(f='ly/clair2.midi', lento=1.0,   ped=1.5, ok=None),
  'moon':  dict(f='ly/moon.midi',   lento=60/50, ped=2.0, ok=None),
  'holst': dict(f='ly/holst.midi',  lento=100/72, ped=1.0, ok={2,3}),
}

def note_di(path, ok):
    m = mido.MidiFile(path); tpb = m.ticks_per_beat
    # mappa del tempo (dal primo track, LilyPond mette i set_tempo lì)
    tempi = []
    for tr in m.tracks:
        t = 0
        for x in tr:
            t += x.time
            if x.type == 'set_tempo': tempi.append((t, x.tempo))
    tempi.sort() or None
    if not tempi or tempi[0][0] > 0: tempi.insert(0, (0, 500000))
    def sec(tick):
        s = 0.0; prev_t, prev_u = 0, tempi[0][1]
        for tt, u in tempi:
            if tt >= tick: break
            s += (tt - prev_t) / tpb * prev_u / 1e6; prev_t, prev_u = tt, u
        return s + (tick - prev_t) / tpb * prev_u / 1e6
    out = []
    for i, tr in enumerate(m.tracks):
        if ok is not None and i not in ok: continue
        t = 0; aperte = {}
        for x in tr:
            t += x.time
            if x.type == 'note_on' and x.velocity > 0:
                aperte.setdefault(x.note, []).append((t, x.velocity))
            elif x.type in ('note_off', 'note_on') and x.note in aperte and aperte[x.note]:
                t0, v = aperte[x.note].pop(0)
                out.append(dict(b0=t0 / tpb, b1=t / tpb, s0=sec(t0), s1=sec(t), p=x.note, v=v, tr=i))
    out.sort(key=lambda n: (n['b0'], n['p']))
    return out

def esegui(nome, cfg, seme=7):
    rnd = random.Random(seme)
    N = note_di(cfg['f'], cfg['ok'])
    trs = sorted({n['tr'] for n in N}); basso_tr = trs[-1]
    fine_b = max(n['b1'] for n in N); fine_s = max(n['s1'] for n in N)
    # tempo che respira: una curva lenta sul tempo (in secondi di partitura), più rallentando negli ultimi quarti
    def t_reale(s, b):
        L = cfg['lento']
        resp = 1 + .035 * math.sin(2 * math.pi * s / 23.0) + .02 * math.sin(2 * math.pi * s / 9.7 + 1.3)
        # integrale approssimato: spostamento proporzionale, abbastanza per una curva lenta
        x = s * L + L * (.035 * 23 / (2 * math.pi) * (1 - math.cos(2 * math.pi * s / 23.0)) + .02 * 9.7 / (2 * math.pi) * (math.cos(1.3) - math.cos(2 * math.pi * s / 9.7 + 1.3)))
        coda = 6.0  # rallentando sugli ultimi 6 quarti
        if b > fine_b - coda:
            k = (b - (fine_b - coda)) / coda
            x += L * (s - s_di_b(fine_b - coda)) * .55 * k * k
        return x
    # per il rallentando serve sapere i secondi di partitura a un dato quarto
    pts = sorted({(n['b0'], n['s0']) for n in N} | {(n['b1'], n['s1']) for n in N})
    def s_di_b(b):
        lo = max((p for p in pts if p[0] <= b), default=pts[0]); return lo[1]
    # gruppi di note attaccate insieme
    gruppi = {}
    for n in N: gruppi.setdefault(round(n['b0'] * 48), []).append(n)
    for g in gruppi.values():
        alto = max(g, key=lambda n: n['p'])
        for n in g:
            d = n['b1'] - n['b0']
            v = 64 + (n['v'] - 90) * .6  # le dinamiche della partitura, dove ci sono
            if n is alto and n['tr'] != basso_tr: v += 14   # la voce in alto canta
            if n['tr'] == basso_tr: v -= 8
            if d >= .99: v += 6
            if d < .45: v -= 10                                  # terzine e arpeggi più leggeri
            v += 7 * math.sin(2 * math.pi * n['s0'] / 17.0)      # piccole onde di intensità per frase
            v += rnd.uniform(-4, 4)
            n['vel'] = max(18, min(118, round(v)))
    # pedale: cambia a ogni periodo; una nota suona fino al primo cambio dopo che il tasto è lasciato
    P = cfg['ped']
    note = []
    for n in N:
        on = t_reale(n['s0'], n['b0'])
        end_b = math.ceil(n['b1'] / P - 1e-6) * P
        if end_b - n['b1'] > P * .999: end_b = n['b1']
        s_end = n['s1'] + (end_b - n['b1']) * (n['s1'] - n['s0']) / max(1e-6, n['b1'] - n['b0']) if n['b1'] > n['b0'] else n['s1']
        off = t_reale(min(s_end, fine_s + 3), min(end_b, fine_b + 3)) + .04
        alto = n['vel'] > 70
        on += rnd.gauss(0, .006) - (.012 if alto else 0)   # la melodia arriva un filo prima, come nei pianisti
        note.append((max(0, on), max(.08, off - on), n['p'], n['vel']))
    note.sort()
    return note

def codifica(note):
    b = bytearray(); prev = 0
    def var(x):
        while True:
            y = x & 127; x >>= 7
            b.append(y | (128 if x else 0))
            if not x: break
    for on, du, p, v in note:
        c = round(on * 100); var(c - prev); prev = c
        var(round(du * 100)); b.append(p); b.append(v)
    return base64.b64encode(bytes(b)).decode()

ris = {}
for k, cfg in BRANI.items():
    nt = esegui(k, cfg)
    ris[k] = codifica(nt)
    print(k, len(nt), 'note', round(nt[-1][0] + nt[-1][1], 1), 's', len(ris[k]), 'byte', 'pitch', min(x[2] for x in nt), max(x[2] for x in nt))
json.dump(ris, open('brani.json', 'w'))
