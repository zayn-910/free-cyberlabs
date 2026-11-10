#!/bin/sh
set -eu

DATA_DIR="${PORTAL_DATA_DIR:-/data}"
RUNTIME_DIR="$DATA_DIR/runtime"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

mkdir -p "$RUNTIME_DIR"
chmod 700 "$RUNTIME_DIR"
umask 077

if [ ! -s "$RUNTIME_DIR/flag" ]; then
  FLAG_TMP="$RUNTIME_DIR/.flag.tmp.$$"
  printf 'FLAG{%s}\n' "$(openssl rand -hex 16)" > "$FLAG_TMP"
  chmod 600 "$FLAG_TMP"
  mv "$FLAG_TMP" "$RUNTIME_DIR/flag"
fi

HASH_TMP="$RUNTIME_DIR/.flag.sha256.tmp.$$"
sha256sum "$RUNTIME_DIR/flag" | cut -d ' ' -f 1 > "$HASH_TMP"
chmod 600 "$HASH_TMP"
mv "$HASH_TMP" "$RUNTIME_DIR/flag.sha256"
chmod 600 "$RUNTIME_DIR/flag"

PORTAL_DATA_DIR="$DATA_DIR" "$SCRIPT_DIR/seed.sh"

exec "$@"
