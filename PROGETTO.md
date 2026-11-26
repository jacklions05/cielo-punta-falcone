# Cielo di Punta Falcone — come è fatto e dove eravamo rimasti

Questo file serve a chi riprende il lavoro: una nuova chat con Claude, Codex o una persona. Va letto prima di toccare il codice.

## Cos'è

Una mappa del cielo interattiva per il sito dell'Associazione Astrofili Piombino (AAP). Mostra il cielo visto dall'osservatorio di Punta Falcone a Piombino con gli oggetti fotografati dai soci. Comprende anche una vista dalla cupola con il telescopio Meade 14″ e una simulazione di cosa si vede all'oculare.

Testi e interfaccia sono in italiano. Il link pubblico è https://jacklions05.github.io/cielo-punta-falcone/ (GitHub Pages dal ramo `main`). Esiste anche l'artifact di claude.ai https://claude.ai/artifact/MMd9qbHARmLsCLhtj56A4Z: **ogni modifica va pubblicata in tutti e due i posti, e i file devono restare identici** (stesso sha256). Prima di pubblicare controlla che l'artifact non sia stato cambiato da un'altra chat: se è cambiato, parti dalla sua versione.

## Com'è organizzato il codice

Tutto sta in `index.html`: HTML, CSS e un unico `<script>` di circa 3,8 MB. Quasi tutto il peso sono dati: stelle Gaia in base64, mappe della Luna piccole, cataloghi. Il codice vero è qualche centinaio di KB.

Fuori dal file ci sono le due mappe della Luna HD e la cartella `piano/` con i campioni del pianoforte, caricate a richiesta con percorso relativo.

### Le parti principali del codice

| Parte | Funzioni / costanti | Note |
|---|---|---|
| **Tempo e astronomia** | `setFromT`, `sidereal`, `sunRaDec`, `moonRaDec`, `planetRaDec`, `posOf`, `vecOf`, `efem` | Calcoli propri, nessuna libreria esterna |
| **Mappa** | `draw`, `redraw`, `proj`, `drawStars`, `drawObjects`, `drawLand`, `drawMilkyWay`, `luciCosta` | Proiezione fisheye dal punto di Punta Falcone, con Elba e costa. Via Lattea: cinque livelli riempiti pari/dispari; i punti oltre 143° dal centro della vista sono portati sul cerchio d = −0,8 allo stesso azimut (prima finivano quasi all'infinito e i lati diventavano rette grigie che tagliavano il cielo in certe direzioni); se l'antipodo è dentro la Via Lattea si inverte il riempimento. Paesaggio (`exa`, `exaK`): al vero con campo sotto i 50°, doppio oltre i 110°, graduale in mezzo; profilo dell'Elba verificato su foto scattate da Punta Falcone (scarto ~0,05°), spalla ovest dopo Marciana corretta; picchi: Calamita, Cima del Monte, Strega, Grosso, Serrone delle Cime, Capanne, Giove, e Monte Cinto in Corsica |
| **Oggetti** | costante oggetti fotografati, `select`, `fillList`, `cardFoto`, `stanotte` | Ogni oggetto ha foto, scheda e link Wikipedia |
| **Lista soci** | `DAFARE`, `PAROLA_SOCI` | Si apre scrivendo "soci" nella ricerca. Tre gruppi: `messier` (Messier non fotografati), `facile` (100 oggetti facili da fotografare), `rasc` (39 della lista RASC Finest NGC). Non compaiono sulla mappa pubblica |
| **Cupola** | `drawCupola`, `fenditura`, `cupVec`, `motoreCupola`, `CUP`, `TEL`, `bersaglioTel`, `drawTelescopio` | Cupola con due ante scorrevoli, telescopio GoTo a 3°/s con rallentamento finale, pulsantiera (velocità, inseguimento, centra, park) |
| **Meteo ed effetti** | `tempesta`, `tempestaOra`, `sorprese`, `FX`, `caccia`, `aereo`, `meteora` | Il temporale chiude la cupola e copre l'oculare |
| **Oculare** | `apriOculare`, `disegnaOculare`, `oggettoOcu`, `OCU_SPECIALI`, `galassiaFisica`, `seeingAvvia`, `stella`, `coloreStella` | Vedi la sezione sotto |
| **Luna all'oculare** | `caricaLuna`, `lunaPixel`, `LUNA_MAPPE` | Illuminazione con il Sole vero, rilievo dal modello del terreno |
| **Didattica** | `sctApri`, `sctTesto`, `sctDisegna` | Tasto "Come funziona il Meade" nella cupola, con due livelli: semplice e approfondito |
| **Timeline** | `TL`, `tlVoci`, `tlMostra`, `tlVoce`, `tlDisegna`, `tlRipresa`, `tlCostVicina`, `TL_CONF` | Pulsante «Timeline» o indirizzo `#timeline`. Un articolo di `PAGINE` per voce, dal più recente; filtri per testo, anno, tipo, costellazione, strumento, sito. La miniatura e il ritaglio di cielo portano all'oggetto sulla mappa (`vaiA`). Data di ripresa letta dal titolo o dall'indirizzo quando c'è. Per Luna, Sole e pianeti la costellazione si calcola alla data con i confini IAU (`TL_CONF`, da d3-celestial) |
| **Confronta** | `CF`, `cfApri`, `cfLato`, `cfSrc` | Tasto «Confronta le foto» nel pannello di un oggetto: due foto in grande affiancate (sul telefono una sopra l'altra), di default la più vecchia e la più recente. Carica l'originale dal sito AAP, poi la versione 720×480, poi la miniatura. Dentro claude.ai le immagini esterne sono bloccate e resta la miniatura |
| **Statistiche soci** | `statSoci` | In cima alla lista soci: articoli, Messier fotografati (contati dalle sigle degli oggetti, comprese le sigle secondarie), articoli per anno, strumenti più usati |
| **Visita l'osservatorio** | `visApri`, `#vis`, `.visFab` | Pulsante «Prenota una visita» sempre visibile in basso a destra (bordo tratteggiato che scorre e pulsa, scritta che luccica, `visFormiche`/`visPulsa`/`visLuccica`, fermi con «riduci movimento»; in cima alla finestra la cupola stilizzata (`img/cupola.jpg`: foto dell'osservatorio ritagliata senza il riquadro UAI, viraggio blu notte–oro, cielo sostituito da un cielo stellato) e il logo AAP (`img/logo.jpg`), la cupola anche sfumata sullo sfondo; le due immagini vanno pubblicate anche nell'artifact) (si nasconde quando è aperto il pannello di un oggetto) o indirizzo `#visita`: prenotazione su WhatsApp ed e-mail (senza testo precompilato, per evitare messaggi mandati per sbaglio), visite@astropiombino.org, indicazioni, sito, Facebook, Instagram, Linktree. Contatti presi da https://linktr.ee/AstroPiombino: se cambiano, vanno aggiornati qui. Prima dei contatti c'è il riquadro `.visInfo` con le regole date dall'associazione (25 nov 2026): cosa si fa, offerta libera, tre schede apribili (serate pubbliche: venerdì da maggio a settembre, poi date annunciate, ~1 h in 1–3 turni, 15–18 persone fino a 20–22, 4 €; gruppi privati: tutto l'anno su richiesta, almeno 2 h, max 12, 50 € a gruppo; scuole: ottobre–giugno, 15–20 ragazzi con insegnanti o genitori, due turni se numerosi, 4 € a ragazzo) e l'invito a scrivere preferibilmente su WhatsApp, con conferma solo alla risposta. Il 26 nov 2026 aggiunte dalle pagine https://web.astropiombino.org/visita-losservatorio/ e /regala-una-serata-sotto-le-stelle/: orari (fine crepuscolo 21–21:30, fino a mezzanotte, turni estivi 21:30 e 22:45), telescopio principale riservato ai gruppi privati, scheda «Regala una serata sotto le stelle», visite di giorno al Sole, scheda «Prima di venire» (sentiero sterrato di 200 m e torcia, vestiti, acqua, cupola da ~20 persone, luci spente, bambini, animali solo nel piazzale, rinvio col maltempo), numero esatto di persone e animali da indicare, link alla pagina del sito. Differenza aperta: il sito dice venerdì pubblici da giugno, il messaggio dell'associazione da maggio (si usa maggio) |
| **Suoni** | `AU`, `suoni`, `sceltaMusica`, `effetti`, `sfx`, `suoniUI` | All'apertura tutto spento. Primo tocco su «Suoni»: parte la musica originale con gli effetti; tocchi successivi aprono il menu. Scelte: Muto, Solo effetti, Musica originale con gli effetti, oppure un brano al pianoforte (Satie, Debussy, Beethoven, Holst) che spegne da solo gli effetti (UFO, meteore, temporale, bip). Casella «Effetti sonori» per riaccenderli; scelta ricordata in localStorage (`pf-effetti`). I brani al pianoforte usano campioni veri: Salamander Grand Piano (Yamaha C5, Alexander Holm, CC BY 3.0), 26 file mp3 in `piano/` (C1–D#7, uno ogni terza minore, ~1,9 MB), scaricati solo alla scelta di un brano (`pianoPrepara`); se non si leggono resta il pianoforte sintetico (`pianoSintetico`). Il volume dei campioni è tarato per suonare forte quanto il sintetico |
| **Schermo intero** | `FS`, `fsCambia`, `fsUI`, `#bFull` | Icona ⛶ in fondo ai comandi (sul telefono nel Menu, con la scritta) e tasto F sul PC; Esc o F per uscire. Su iPhone il browser non permette lo schermo intero e l'icona resta nascosta: lì si usa Condividi → Aggiungi a schermata Home (meta `apple-mobile-web-app-capable`). Dentro il sito AAP serve `allowfullscreen` sull'iframe |
| **Supernove** | `SUPERNOVE`, `snTag`, `CATALOGHI.SN` | Sigle ufficiali legate alla galassia ospite, senza creare oggetti nuovi sulla mappa: dal sito storico SN 2011fe e SN 2023ixf (M101), SN 2012aw (M95, oggetto M96G), SN 2013am (M65, Tripletto del Leone), SN 2013df (NGC 4414), SN 2013ev (IC 1296), SN 2014J (M82), SN 2014bc (M106), SN 2017eaw (NGC 6946); dal sito attuale SN 2020jfo (M61), SN 2026fvx (NGC 4205), SN 2026kid (NGC 5907), SN 2026aaiv (NGC 7331). La sigla entra tra i cataloghi dell'oggetto: si cerca (anche senza «SN» o senza spazio), compare nel filtro «Supernove» della lista e nella timeline, e il pannello della galassia la mostra. Per una nuova supernova basta una riga in `SUPERNOVE` |
| **Serate (soci)** | `SNR`, `SES`, `sesApri`, `sesNotte`, `sesMeteo`, `sesSeeing`, `sesBlocchi`, `sesServe`, `sesFatte`, `sesDisegnaTempo`, `sesDisegnaPiano`, `sesDisegnaProgetti`, `sesSalva`, `sesCaricaTutte` | Si apre scrivendo «astro» nella ricerca, o con `#serata` (non più dalla lista soci, che resta per gli oggetti mancanti). Ispirato a NINA: per la notte scelta meteo essenziale (Open-Meteo, fino a 16 giorni; seeing stimato dai venti in quota) e link a meteoblue e meteoeradar; **linea del tempo** con due file, TDIG + Zeus 455M e GSO + ASI2600MC, oggetti a cascata come barre (durata = Σ pose × (posa + tempo morto)), dietro ogni barra la curva d'altezza calcolata dalla mappa, linea dei 30°, crepuscolo in grigio, bordo rosso se si va oltre l'alba. Per ogni oggetto righe filtro · posa · numero, μ media precompilata da OCU_DATI (magnitudine e assi) e sostituibile incollando un valore trovato col link (sotto 18 è in mag/′² e si aggiunge 8,89). Riepilogo per filtro: prima (serate segnate come fatte), stasera (pose × posa × (1 − scarto)), totale, servono (motore SNR: SNR scelto, di base 20, su 2″×2″ a μ + 1,5, cielo SQM 20,15 più la Luna a metà blocco), mancano. Opzioni: inizio, tempo morto (2 s), pose scartate (20%), cielo, SNR. File JSON versione 2 in `jacklions05/cielo-punta-falcone-sessioni/serate/` (token spezzato in `sesTk`), apribili e riscrivibili (sha); casella «Serata fatta» per farle contare; tabella «Progetti» con le ore utili accumulate per oggetto, strumento e filtro |
| **Apri e chiudi** | `TOCCO`, ascoltatori in fondo allo script | Un tocco fuori (senza trascinare) chiude menu e livelli; un tocco sul cielo vuoto chiude anche il pannello; trascinare, pizzicare o usare la rotellina non chiude niente. Esc chiude solo lo strato più in alto (confronto, oculare o Meade, timeline, menu, pannello). Toccare lo sfondo intorno a oculare e Meade li chiude. Testo non selezionabile per sbaglio (`user-select:none`), tranne campi e testi informativi |

### L'oculare: le scelte importanti

- **Telescopio:** Meade 14″ ACF, D = 356 mm, F = 2845 mm (f/8), costante `FOC_MEADE`.
- **Oculari veri della cupola** (`OCULARI`, focale in mm e campo apparente in gradi): 40 mm Plössl 45°, 34 mm 64°, 26 mm Plössl 45°, 20 mm 64°, 14 mm 82°. In più 8, 5 e 3,5 mm a 82°, immaginari, disponibili per tutti gli oggetti (`OCU_LUNA` è l'indice del primo, non serve più a nascondere niente). **Il cerchio disegnato è proporzionale al campo apparente** (`AFOV_MAX = 82`), così confrontare oculari diversi è corretto.
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

## Pubblicazione, versioni e repository (tolto dal README pubblico)

**Inserirla nel sito AAP.** Basta un iframe in una pagina del sito, che mostra sempre l'ultima versione pubblicata:

```html
<iframe src="https://jacklions05.github.io/cielo-punta-falcone/"
        style="width:100%; height:85vh; border:0" allowfullscreen></iframe>
```

In alternativa un link o pulsante allo stesso indirizzo.

**Versioni precedenti.** Ogni modifica resta nei *Commits*. Per riaprire una versione vecchia: `https://raw.githack.com/jacklions05/cielo-punta-falcone/<codice-commit>/index.html` (al primo accesso githack chiede *Open the page*). Le versioni importanti si possono segnare con un tag (*Releases*, es. `v1`) e usare il nome al posto del codice.

**Aprirla dal computer.** *Code → Download ZIP* e apri `index.html`: funziona tutto tranne la Luna HD, perché il browser blocca le immagini lette da file; resta la Luna normale.

**Contenuto del repository.**

| Percorso | Cosa contiene |
|---|---|
| `index.html` | La mappa intera (circa 4 MB, quasi tutto dati) |
| `luna_alb_hd.jpg`, `luna_pend_hd.jpg` | Luna HD (albedo e pendenze, NASA LRO), caricate solo quando servono |
| `img/` | Cupola stilizzata e logo AAP per la finestra «Prenota una visita» |
| `piano/` | Campioni del pianoforte per i brani classici (Salamander Grand Piano, CC BY 3.0): vanno pubblicati anche nell'artifact |
| `docs/oculare-simulazioni.pdf` | Tutte le simulazioni all'oculare |
| `strumenti/`, `strumenti/dati/` | Script Python e dati di partenza (OpenNGC, stelle Gaia estratte, campi) |
| `PROGETTO.md` | Questa guida |

**Fonti.** Stelle deboli: Gaia DR3 dal catalogo locale di Siril. Stelle brillanti: d3-celestial (Hipparcos/BSC). Oggetti: OpenNGC (CC-BY-SA 4.0). Luna all'oculare: NASA LRO (LROC WAC, LOLA LDEM). Posizioni di Sole, Luna e pianeti calcolate nella pagina, i pianeti con gli elementi orbitali approssimati del JPL (Standish). Taratura delle simulazioni su schizzi di asod.info, solo come riferimento: **non citarlo nelle pagine pubbliche**, lì si dice solo che le viste sono simulate.

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
- **Guida pubblica:** questo file è pubblico; niente nomi di persone né racconti delle richieste.
- **Commit:** titoli brevi e neutri (es. «Aggiornamento mappa», «Correzioni»), senza descrivere le richieste o le conversazioni e senza nomi. I dettagli di cosa è cambiato stanno in questa guida, non nei commit.
- I nomi degli oggetti nella lista soci finiscono con `X` (Messier e facili) o `R` (RASC).


## Sicurezza (controllo del 26 nov 2026)

- **Token delle serate.** Sta nella pagina pubblica (spezzato e capovolto in `sesTk`, solo per non farlo riconoscere da GitHub: chi legge il codice lo ricostruisce). Permessi: solo `jacklions05/cielo-punta-falcone-sessioni`, Contents lettura/scrittura, scadenza 23 febbraio 2027. Non può toccare la mappa, altri repository, l'account o i workflow. Rischi che restano: chi lo copia può scrivere, cambiare o cancellare file nel repository delle sessioni e consumare la quota di 5000 richieste l'ora del token. Rimedi: la cronologia di git conserva tutto; si revoca e si sostituisce in un minuto.
- **Letture senza token.** L'elenco delle serate usa l'API pubblica (quota di 60 richieste l'ora per ogni visitatore), i file arrivano da raw.githubusercontent.com. Il token serve solo per salvare.
- **Pulizia dei file letti** (`sesPulisci`): solo campi noti, oggetti del catalogo, filtri dello strumento, numeri entro limiti, testi senza caratteri HTML; tutto ciò che va in pagina passa da `sesEsc`. Un file costruito apposta non può iniettare codice nella mappa.
- **Controllo automatico nel repository delle sessioni** (`strumenti/sessioni/controllo.yml`, da mettere in `.github/workflows/controllo.yml` del repository delle sessioni): a ogni modifica toglie file fuori da `serate/`, più grandi di 30 KB o non conformi. Il token della mappa non può modificarlo (serve il permesso workflows).
- **Nessun dato personale** nelle sessioni: solo nickname. Le prenotazioni restano fuori.
- **Mappa**: nessun dato degli utenti; GoatCounter senza cookie; link esterni con `rel="noopener"`.

## Cose aperte / idee

- Mappa della Luna più fine (Kaguya 64 pixel/grado): valutata e scartata. Con gli oculari veri la mappa attuale è già più fine dello schermo; il guadagno ci sarebbe solo col 5 e 3,5 mm a seeing spento.
- Timeline: la data di ripresa c'è solo per circa un terzo degli articoli, quelli che la scrivono nel titolo o nell'indirizzo.
- Il ramo ovest del Velo (NGC 6960) è al limite della visibilità: da verificare con chi lo osserva dalla cupola.
- M101, M31 e altri oggetti grandi e deboli non hanno uno schizzo di riferimento con un cielo simile al nostro.
- Il valore esatto del rapporto f del primario e dell'ingrandimento del secondario del Meade 14″ f/8 non è confermato: nella didattica ci sono solo stime.
- Nuove foto: si aggiungono a mano (riga in `PAGINE`, miniatura in `TH`/`IMG`). Aggiornamento automatico, filtro per autore e dati tecnici delle riprese: valutati e scartati.
- **Statistiche di utilizzo (attive dal 25 nov 2026):** GoatCounter, codice `jacklionse` (https://jacklionse.goatcounter.com). Lo script si carica in cima alla pagina; `conta(path,title)` registra eventi: `oggetto/<id>` quando si apre un oggetto, `prenota/apre`, `prenota/whatsapp`, `prenota/email`. Esclusione: aprire una volta `#non-contarmi` su ogni browser/dispositivo (segno `pf-noconta` in localStorage, il contatore non viene caricato); `#conta-di-nuovo` lo toglie. Nell'artifact di claude.ai il contatore è bloccato e non conta. Dentro l'iframe del sito AAP alcuni browser tengono una memoria separata: lì l'esclusione va rifatta aprendo `#non-contarmi` nella pagina AAP solo se l'iframe usa quell'indirizzo, altrimenti si usa «Ignore IPs» di GoatCounter.
- **Modulo sessioni di astrofotografia (linea del tempo e ore accumulate fatte il 25 nov 2026; manca il controllo GitHub Actions):** planner della notte (meteo Open-Meteo, seeing 7Timer, Luna, buio, oggetti migliori), motore delle ore dal vecchio calcolatore «SNR TDIG vs GSO» (artifact UzvPXe4qsWV3Mr1bZxzZGr), catalogo esteso, sequenza della serata tipo NINA, chiusura con pose fatte e ore mancanti. Strumenti fissi: GSO + ASI2600MC (nessun filtro o dual-band Ha/OIII), TDIG + Zeus 455M (L, R, G, B, Ha, OIII, SII). Mosaico escluso. Dati salvati come file di testo nel repository pubblico separato `jacklions05/cielo-punta-falcone-sessioni`, scritti dalla mappa con un token fine-grained «mappa-sessioni» (solo quel repository, Contents read/write; verificato il 25 nov 2026). **Il token scade il 23 febbraio 2027**: va rigenerato e sostituito nella pagina. Il token non va mai scritto in chiaro in un file del repository (GitHub lo revoca da solo): nella pagina va spezzato. Previsto un controllo con GitHub Actions che toglie i file non validi. Le prenotazioni NON vanno in questo repository (dati personali): sistema a parte, quando l'associazione darà le regole.
- Si potrebbe spezzare `index.html` in più file (codice, dati, stile), così le modifiche toccano solo poche righe.
