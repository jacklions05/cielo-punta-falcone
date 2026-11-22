# Cielo di Punta Falcone — come è fatto e dove eravamo rimasti

Questo file serve a chi riprende il lavoro: una nuova chat con Claude, Codex o una persona. Va letto prima di toccare il codice.

## Cos'è

Una mappa del cielo interattiva per il sito dell'Associazione Astrofili Piombino (AAP). Mostra il cielo visto dall'osservatorio di Punta Falcone a Piombino con gli oggetti fotografati dai soci. Comprende anche una vista dalla cupola con il telescopio Meade 14″ e una simulazione di cosa si vede all'oculare.

Testi e interfaccia sono in italiano. Il link pubblico è https://jacklions05.github.io/cielo-punta-falcone/ (GitHub Pages dal ramo `main`). Esiste anche l'artifact di claude.ai https://claude.ai/artifact/MMd9qbHARmLsCLhtj56A4Z: **ogni modifica va pubblicata in tutti e due i posti, e i file devono restare identici** (stesso sha256). Prima di pubblicare controlla che l'artifact non sia stato cambiato da un'altra chat: se è cambiato, parti dalla sua versione.

## Com'è organizzato il codice

Tutto sta in `index.html`: HTML, CSS e un unico `<script>` di circa 3,8 MB. Quasi tutto il peso sono dati: stelle Gaia in base64, mappe della Luna piccole, cataloghi. Il codice vero è qualche centinaio di KB.

Fuori dal file ci sono solo le due mappe della Luna HD, caricate a richiesta con percorso relativo.

### Le parti principali del codice

| Parte | Funzioni / costanti | Note |
|---|---|---|
| **Tempo e astronomia** | `setFromT`, `sidereal`, `sunRaDec`, `moonRaDec`, `planetRaDec`, `posOf`, `vecOf`, `efem` | Calcoli propri, nessuna libreria esterna |
| **Mappa** | `draw`, `redraw`, `proj`, `drawStars`, `drawObjects`, `drawLand`, `drawMilkyWay`, `luciCosta` | Proiezione fisheye dal punto di Punta Falcone, con Elba e costa |
| **Oggetti** | costante oggetti fotografati, `select`, `fillList`, `cardFoto`, `stanotte` | Ogni oggetto ha foto, scheda e link Wikipedia |
| **Lista soci** | `DAFARE`, `PAROLA_SOCI` | Si apre scrivendo "soci" nella ricerca. Tre gruppi: `messier` (Messier non fotografati), `facile` (100 oggetti facili da fotografare), `rasc` (39 della lista RASC Finest NGC). Non compaiono sulla mappa pubblica |
| **Cupola** | `drawCupola`, `fenditura`, `cupVec`, `motoreCupola`, `CUP`, `TEL`, `bersaglioTel`, `drawTelescopio` | Cupola con due ante scorrevoli, telescopio GoTo a 3°/s con rallentamento finale, pulsantiera (velocità, inseguimento, centra, park) |
| **Meteo ed effetti** | `tempesta`, `tempestaOra`, `sorprese`, `FX`, `caccia`, `aereo`, `meteora` | Il temporale chiude la cupola e copre l'oculare |
| **Oculare** | `apriOculare`, `disegnaOculare`, `oggettoOcu`, `OCU_SPECIALI`, `galassiaFisica`, `seeingAvvia`, `stella`, `coloreStella` | Vedi la sezione sotto |
| **Luna all'oculare** | `caricaLuna`, `lunaPixel`, `LUNA_MAPPE` | Illuminazione con il Sole vero, rilievo dal modello del terreno |
| **Didattica** | `sctApri`, `sctTesto`, `sctDisegna` | Tasto "Come funziona il Meade" nella cupola, con due livelli: semplice e approfondito |
| **Timeline** | `TL`, `tlVoci`, `tlMostra`, `tlVoce`, `tlDisegna`, `tlRipresa`, `tlCostVicina`, `TL_CONF` | Pulsante «Timeline» o indirizzo `#timeline`. Un articolo di `PAGINE` per voce, dal più recente; filtri per testo, anno, tipo, costellazione, strumento, sito. La miniatura e il ritaglio di cielo portano all'oggetto sulla mappa (`vaiA`). Data di ripresa letta dal titolo o dall'indirizzo quando c'è. Per Luna, Sole e pianeti la costellazione si calcola alla data con i confini IAU (`TL_CONF`, da d3-celestial) |

### L'oculare: le scelte importanti

- **Telescopio:** Meade 14″ ACF, D = 356 mm, F = 2845 mm (f/8), costante `FOC_MEADE`.
- **Oculari veri della cupola** (`OCULARI`, focale in mm e campo apparente in gradi): 40 mm Plössl 45°, 34 mm 64°, 26 mm Plössl 45°, 20 mm 64°, 14 mm 82°. In più 8, 5 e 3,5 mm a 82°, immaginari, solo per la Luna: `OCU_LUNA` è l'indice del primo. **Il cerchio disegnato è proporzionale al campo apparente** (`AFOV_MAX = 82`), così confrontare oculari diversi è corretto.
- **Cielo:** SQM 20,15 (Bortle circa 5), da lightpollutionmap. Due fondi, scelti col tasto «Fondo grigio» (`OCU.scuro`, ricordato in localStorage): grigio come uno schizzo, oppure scuro come all'oculare, con luminosità che va come il quadrato della pupilla d'uscita.
- **Stelle:**
  - entro 0,5° da ogni oggetto sono **vere**, da Gaia DR3: `GAIA_B64` compresso, `GAIA_CAMPI` contiene i centri dei campi coperti;
  - più lontano sono inventate ma sempre uguali nello stesso punto (generatore `rngDa` per cella);
  - colori dalla temperatura (B−V, tabella di corpo nero `COL_BV`), pieni fino a mag 6,5, poi sfumano fino al bianco alla mag 9; intensità ×1,6 per il contrasto percepito.
- **Doppie** (`DOPPIE`, `DOPPIE_POS`): compagne dai dati WDS, primarie in posizione esatta Hipparcos. `skipDoppie` evita di disegnarle due volte.
- **Galassie generiche:** `galassiaFisica` usa un modello fisico (disco esponenziale più bulge) con la magnitudine e il tipo di Hubble da OpenNGC, e la soglia di contrasto dell'occhio.
- **Oggetti speciali** disegnati a mano in `OCU_SPECIALI`: M13, M57, M27, M82, M81, M1, M104, M31, M51, M42, M17, M8. Più il Velo (N6960, N6992) nel ramo generico.
- **Seeing:** in WebGL (`SEE`, `seeingGL`): campo di spostamento continuo a più scale che scorre col vento (frozen flow), ballo d'insieme, sfocatura grande quanto il disco di seeing (FWHM 1,5–3″, × massa d'aria^0,6) e brevi istanti di calma. Senza WebGL resta il vecchio metodo a strisce (`seeingStrisce`). Si può spegnere.
- **Cupola chiusa o puntata fuori dalla fenditura:** l'oculare si oscura (`fenditura(v)`). Vale solo se l'oculare è aperto dal telescopio (`OCU.daTel`). Dal pannello di un oggetto è solo un'anteprima.
- **Taratura:** alcuni oggetti sono stati confrontati con schizzi di asod.info fatti con aperture e cieli simili: M51 e M33 (Ikebe), M82, M42, M57, M27, M17, M8 (Ikebe), Velo (Ikebe). Gli schizzi non sono stati copiati.

## Dati e come rigenerarli (`strumenti/`)

| Script | Cosa fa |
|---|---|
| `estrai_gaia.py` | **Gira sul PC con Siril.** Legge il catalogo locale `%LOCALAPPDATA%\siril\siril_cat_healpix8_astro.dat` (formato HEALPix livello 8, record di 16 byte) ed estrae le stelle fino a G 14,8 entro 0,5° dai campi dati (`dati/tl.json`, `dati/tl2.json`) |
| `packgaia.py` | Unisce le stelle (`dati/gaia_tutti.json`), toglie i doppioni delle stelle brillanti e delle doppie, comprime in `gaia_b64.txt`: 8 byte a stella, gzip e base64. Il risultato va incollato in `GAIA_B64` |
| `ocu.py` | Costruisce i dati degli oggetti (`OCU_DATI`) da OpenNGC. Attenzione: per alcune galassie la magnitudine V di OpenNGC è sbagliata, e si usa B − 0,8 |
| `costruisci_luna.py` | Crea `luna_alb_hd.jpg` e `luna_pend_hd.jpg` dalle mappe NASA (le sorgenti sono indicate nello script) |
| `simulazioni.py` + `pdf.py` | Renderizzano tutti gli oggetti all'oculare e creano `docs/oculare-simulazioni.pdf` |
| `smoke.py` | Test automatico di quasi tutta l'interfaccia, a misura PC (Playwright, serve `python -m http.server 8765` nella cartella) |
| `t64.py` | Rende un singolo oggetto: `python t64.py M42:2,M57:4`, dove il numero è l'indice in `OCULARI` |

Gli script usano Python 3 con numpy, Pillow, reportlab, playwright e healpy (solo per verifiche).

## Regole pratiche per modificare

- Dopo ogni modifica controlla la sintassi: estrai lo script e lancia `node --check`. Un commento `//` messo a metà riga ha già rotto tutto una volta: dentro le righe lunghe usa `/* */`.
- Prova l'oculare con `t64.py` o `simulazioni.py` prima di pubblicare.
- Il file deve iniziare con `<!DOCTYPE html>`.
- I nomi degli oggetti nella lista soci finiscono con `X` (Messier e facili) o `R` (RASC).

## Cose aperte / idee

- Mappa della Luna più fine (Kaguya 64 pixel/grado): valutata e scartata. Con gli oculari veri la mappa attuale è già più fine dello schermo; il guadagno ci sarebbe solo col 5 e 3,5 mm a seeing spento.
- Timeline: la data di ripresa c'è solo per circa un terzo degli articoli, quelli che la scrivono nel titolo o nell'indirizzo.
- Il ramo ovest del Velo (NGC 6960) è al limite della visibilità: da verificare con chi lo osserva dalla cupola.
- M101, M31 e altri oggetti grandi e deboli non hanno uno schizzo di riferimento con un cielo simile al nostro.
- Il valore esatto del rapporto f del primario e dell'ingrandimento del secondario del Meade 14″ f/8 non è confermato: nella didattica ci sono solo stime.
- Si potrebbe spezzare `index.html` in più file (codice, dati, stile), così le modifiche toccano solo poche righe.
