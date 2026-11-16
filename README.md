# Cielo di Punta Falcone

Mappa del cielo interattiva per il sito dell'Associazione Astrofili Piombino (AAP): il cielo visto dall'osservatorio di Punta Falcone, con gli oggetti fotografati dai soci, la cupola con il Meade 14″ e la simulazione di come appaiono gli oggetti all'oculare.

## Apri la mappa

### 👉 **https://jacklions05.github.io/cielo-punta-falcone/**

Si apre direttamente nel browser, senza scaricare niente, anche da telefono. È pubblicata con GitHub Pages dal ramo `main`: ogni modifica caricata qui è online dopo circa un minuto.

Per aprire la mappa già centrata su un oggetto, aggiungi in fondo `#` e il nome senza spazi, per esempio [`…/cielo-punta-falcone/#M42`](https://jacklions05.github.io/cielo-punta-falcone/#M42).

## Inserirla nel sito dell'associazione

Basta incollare in una pagina del sito questo codice, che mostra la mappa dentro la pagina:

```html
<iframe src="https://jacklions05.github.io/cielo-punta-falcone/"
        style="width:100%; height:85vh; border:0" allowfullscreen></iframe>
```

In alternativa si mette un semplice link o pulsante all'indirizzo sopra. In entrambi i casi il sito mostra sempre l'ultima versione pubblicata qui, senza doverlo aggiornare.

## Vedere le versioni precedenti

Ogni modifica resta nella cronologia del repository (scheda *Commits*). Per riaprire online una versione vecchia, prendi il codice del commit (il lungo codice esadecimale) e apri:

```
https://raw.githack.com/jacklions05/cielo-punta-falcone/<codice-commit>/index.html
```

Al primo accesso compare una pagina di avviso di githack: si clicca *Open the page*. Le versioni importanti si possono anche segnare con un nome (*Releases → tag*, per esempio `v1`), e il nome si usa al posto del codice.

## Aprirla dal computer

Puoi anche scaricare il repository (*Code → Download ZIP*) e aprire `index.html`. Funziona tutto tranne la Luna in alta risoluzione, perché il browser blocca la lettura delle immagini aperte da file: resta la Luna a risoluzione normale.

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
