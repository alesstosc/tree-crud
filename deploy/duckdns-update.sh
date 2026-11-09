#!/bin/bash
# Aggiorna il record A di <dominio>.duckdns.org con l'IP pubblico corrente.
#
# Nota di sicurezza: il token DuckDNS e' una chiave condivisa e deve essere
# inviato in chiaro al server (su HTTPS). Questo script evita pero' che finisca
# sulla command line (visibile con `ps`): la richiesta viene passata a curl
# via stdin con `-K -`, quindi argv resta pulito.
set -uo pipefail
umask 077

CONF=/etc/duckdns/duckdns.conf
[ -r "$CONF" ] || { logger -t duckdns "config $CONF non leggibile"; exit 1; }
# shellcheck disable=SC1090
. "$CONF"

: "${DUCKDNS_TOKEN:?token mancante}"
# Supporta sia DUCKDNS_DOMAINS (lista) sia il vecchio DUCKDNS_DOMAIN
DOMAINS="${DUCKDNS_DOMAINS:-${DUCKDNS_DOMAIN:-}}"
: "${DOMAINS:?dominio mancante}"

# IP pubblico (con fallback su servizi alternativi)
IP=""
for url in https://api.ipify.org https://ifconfig.me/ip https://icanhazip.com; do
    IP=$(curl -4 -fsS --max-time 10 "$url" 2>/dev/null | tr -d '[:space:]')
    [[ "$IP" =~ ^[0-9]{1,3}(\.[0-9]{1,3}){3}$ ]] && break
    IP=""
done
if [ -z "$IP" ]; then
    logger -t duckdns "impossibile determinare l'IP pubblico"
    exit 1
fi

# URL costruito e consegnato a curl via stdin: non appare in /proc/<pid>/cmdline
RESP=$(printf 'url = "https://www.duckdns.org/update?domains=%s&token=%s&ip=%s"\n' \
        "$DOMAINS" "$DUCKDNS_TOKEN" "$IP" \
       | curl -fsS --max-time 15 --proto '=https' -K - 2>/dev/null)

unset DUCKDNS_TOKEN

case "$RESP" in
    OK*)  logger -t duckdns "OK: ${DOMAINS}.duckdns.org -> ${IP}"; exit 0 ;;
    KO*)  logger -t duckdns "ERRORE: risposta KO dal server DuckDNS (token/dominio?)"; exit 1 ;;
    *)    logger -t duckdns "ERRORE: risposta inattesa: ${RESP:-vuota}"; exit 1 ;;
esac
