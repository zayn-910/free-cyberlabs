#!/bin/sh
set -eu
DIR=/run/lab
mkdir -p "$DIR"
if [ ! -f "$DIR/receipt" ]; then
  umask 077
  value=$(printf 'FL''AG{%s}' "$(openssl rand -hex 16)")
  printf '%s' "$value" > "$DIR/receipt"
  printf '%s' "$value" | sha256sum | cut -d' ' -f1 > "$DIR/receipt.sha256"
  chmod 0600 "$DIR/receipt" "$DIR/receipt.sha256"
fi
/srv/scripts/seed.sh
exec "$@"
