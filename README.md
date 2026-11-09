# Tree CRUD

Mappa ad albero a file singolo (Python + HTML/JS) con assistente IA basato su
**DeepSeek** che suggerisce nuove ramificazioni — figli e fratelli — coerenti
con la tassonomia del progetto.

Il progetto vive su **https://tree-crud.duckdns.org** (demo pubblica).

## Funzionalità

- **Albero CRUD**: crea, rinomina, elimina nodi; note per ogni nodo; struttura
  annidata illimitata.
- **IA DeepSeek**:
  - `+ Figlio` e `+ Fratello` interrogano il modello e propongono almeno 3
    suggerimenti basati sull'intero albero (tronco, rami e note).
  - Per i *fratelli* il modello è costretto a individuare prima la **categoria
    tassonomica** dei fratelli esistenti e a proporre solo elementi della stessa
    categoria e granularità (es. con `Preistoria / Medioevo / Evo Contemporaneo`
    propone `Evo Antico / Evo Moderno`, non sotto-argomenti come
    "Metallurgia e reti di scambio").
  - Dedup automatico (mai nomi già presenti allo stesso livello) e dedup tra le
    proposte.
  - Selezione multipla con checkbox e accettazione unica; campo per nome
    personalizzato; fallback manuale se la chiamata fallisce.
- **Regole Tree**: pannello per editare a piacere le regole che la IA segue per
  generare i suggerimenti (salvate nel browser).
- **Drag & drop**: riordino dei rami tra fratelli (stesso livello), gli altri
  nodi scorrono di conseguenza.
- **Carica JSON / Export JSON**: il progetto si salva e si ricarica per
  continuare il lavoro. L'import è sanitizzato (vedi Sicurezza).
- Persistenza locale dell'albero (`localStorage`).

## Architettura

- **Backend**: un solo file Python (`tree-crud.py`) — `ThreadingHTTPServer` su
  `127.0.0.1:8080` che serve una pagina HTML/JS inline. Nessuna dipendenza
  esterna, nessun database.
- **Frontend**: HTML/CSS/JS vanilla, tutto inline.
- **IA**: chiamate **dirette dal browser** a `https://api.deepseek.com`
  (modelli `deepseek-chat` e `deepseek-reasoner`). La API key resta nel browser
  e **non passa mai dal server**.

## Avvio locale

```bash
python3 tree-crud.py
# → http://localhost:8080/
```

Poi clicca **IA**, inserisci la tua API key DeepSeek e scegli il modello.
La chiave viene salvata nel browser (checkbox per non persisterla).

## Deploy online

Guida completa per metterlo in produzione dietro nginx con HTTPS
(percorsi e unit usati per `tree-crud.duckdns.org`, Armbian/noble).

### 1. DNS dinamico (DuckDNS)

Crea un account su [duckdns.org](https://www.duckdns.org) e il sottodominio
desiderato. Sul server:

```bash
install -m 700 -d /etc/duckdns
cat > /etc/duckdns/duckdns.conf <<'EOF'
DUCKDNS_TOKEN=IL_TUO_TOKEN
DUCKDNS_DOMAINS=tuo-sottodominio
EOF
install -m 755 deploy/duckdns-update.sh /usr/local/bin/duckdns-update.sh
install -m 644 deploy/duckdns.service deploy/duckdns.timer /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now duckdns.timer
/usr/local/bin/duckdns-update.sh   # aggiornamento immediato
```

Lo script aggiorna l'IP ogni 5 minuti e non espone mai il token sulla
command line (passa l'URL a curl via stdin).

### 2. Firewall

```bash
ufw allow 80/tcp    # HTTP / ACME
ufw allow 443/tcp   # HTTPS
```

### 3. Applicazione

```bash
install -m 755 -d /opt/tree-crud
install -m 644 tree-crud.py /opt/tree-crud/tree-crud.py
install -m 644 deploy/tree-crud.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now tree-crud
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8080/   # atteso: 200
```

Il servizio gira come `www-data` in ascolto solo su loopback.

### 4. nginx

```bash
install -m 644 deploy/tree-crud.nginx.conf /etc/nginx/sites-available/tree-crud
ln -s /etc/nginx/sites-available/tree-crud /etc/nginx/sites-enabled/tree-crud
nginx -t && systemctl reload nginx
```

Sostituisci `tree-crud.duckdns.org` con il tuo dominio nel file di configurazione.

### 5. HTTPS (Let's Encrypt)

```bash
certbot --nginx -d tree-crud.duckdns.org --non-interactive --agree-tos --redirect
certbot renew --dry-run   # verifica rinnovo automatico
```

### 6. Verifica

```bash
curl -sI http://tree-crud.duckdns.org/   # atteso: 301 → https
curl -sI https://tree-crud.duckdns.org/  # atteso: 200
```

## Configurazione IA nell'app

1. Apri il sito, clicca **IA**.
2. Inserisci la API key DeepSeek e scegli il modello
   (`deepseek-chat` consigliato; con `deepseek-reasoner` il client omette
   `response_format`/`temperature` perché non supportati).
3. Opzionale: **Regole Tree** per personalizzare le istruzioni dell'IA.
4. Seleziona un nodo e premi `+ Figlio` o `+ Fratello`: l'IA propone almeno 3
   rami, scegli con le checkbox e conferma con "Aggiungi selezionati".

## Sicurezza

- **API key DeepSeek**: vive solo nel browser (`localStorage`, o
  `sessionStorage` se deselezioni "Ricorda"); è inviata esclusivamente a
  `api.deepseek.com` via HTTPS e non transita dal server.
- **XSS**: l'import JSON è sanitizzato (id ricostruiti come interi, struttura
  validata) e il render forza id numerici; titoli e note sono sempre escapati o
  scritti con `textContent`. Anche i dati legacy in `localStorage` vengono
  risanati al caricamento.
- **Header nginx** (nel vhost di esempio): HSTS, CSP con
  `connect-src https://api.deepseek.com`, `X-Content-Type-Options`,
  `Referrer-Policy`, `X-Frame-Options`, `Permissions-Policy`.
- **Limiti noti**: la chiave è leggibile dagli strumenti di sviluppo e da
  estensioni del browser; non usare l'app su macchine condivise con la chiave
  persistita. La CSP usa `'unsafe-inline'` perché l'app è interamente inline:
  è difesa in profondità, non un sandbox.

## Struttura del repository

```
tree-crud.py            # applicazione (unico file)
deploy/
  tree-crud.service     # unit systemd dell'app
  tree-crud.nginx.conf  # vhost nginx (HTTP→HTTPS + proxy + header di sicurezza)
  duckdns.service       # unit di aggiornamento DNS
  duckdns.timer         # timer (ogni 5 minuti)
  duckdns-update.sh     # script di aggiornamento del record A
```
