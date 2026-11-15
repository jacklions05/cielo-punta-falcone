# Cielo di Punta Falcone

Mappa del cielo interattiva per il sito dell'Associazione Astrofili Piombino (AAP): il cielo visto dall'osservatorio di Punta Falcone, con gli oggetti fotografati dai soci, la cupola con il Meade 14″ e la simulazione di come appaiono gli oggetti all'oculare.

## Come si apre

- **In locale:** apri `index.html` nel browser. Tutto funziona tranne la Luna in alta risoluzione: il browser blocca la lettura delle immagini aperte da file, e resta la Luna a risoluzione normale.
- **Online con GitHub Pages:** Settings → Pages → *Deploy from a branch* → `main` / root. La mappa sarà su `https://<utente>.github.io/cielo-punta-falcone/`, con la Luna HD.

## Cosa c'è nel repository

| Percorso | Cosa contiene |
|---|---|
| `index.html` | La mappa intera: pagina, stile, codice e dati in un solo file (circa 4 MB, quasi tutto dati) |
| `luna_alb_hd.jpg`, `luna_pend_hd.jpg` | La Luna in alta risoluzione (albedo e pendenze del terreno, NASA LRO); si caricano solo quando serve |
| `docs/oculare-simulazioni.pdf` | Tutte le simulazioni all'oculare, una per oggetto |
| `strumenti/` | Script Python usati per costruire i dati e per i test |
| `strumenti/dati/` | Dati di partenza: catalogo OpenNGC, stelle Gaia estratte, elenchi dei campi |
| `PROGETTO.md` | Come è fatto il progetto, le scelte prese e cosa resta da fare. **Da leggere prima di modificare** |

## Fonti dei dati

- Stelle deboli: Gaia DR3, dal catalogo locale di Siril (`siril_cat_healpix8_astro.dat`)
- Stelle brillanti: catalogo d3-celestial (Hipparcos/BSC)
- Oggetti: OpenNGC (licenza CC-BY-SA 4.0)
- Luna: NASA LRO (LROC WAC, LOLA LDEM)
- Taratura delle simulazioni: schizzi di Astronomy Sketch of the Day (asod.info), usati solo come riferimento e non copiati
