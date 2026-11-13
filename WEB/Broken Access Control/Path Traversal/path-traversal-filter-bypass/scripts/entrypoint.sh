#!/bin/sh
set -eu

FLAG_FILE="/app/flag.txt"
HASH_FILE="/app/flag.sha256"

if [ ! -f "$FLAG_FILE" ]; then
  umask 077
  RAW=$(openssl rand -hex 16)
  printf 'FLAG{%s}' "$RAW" > "$FLAG_FILE"
  sha256sum "$FLAG_FILE" | cut -d' ' -f1 > "$HASH_FILE"
fi

exec "$@"
