#!/bin/sh
set -eu
if [ "$#" -ne 1 ]; then
  echo "usage: ./verify.sh <submitted-value>" >&2
  exit 2
fi
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
actual=$(printf '%s' "$1" | docker compose -f "$ROOT/docker-compose.yml" exec -T app python -c 'import hashlib,sys; print(hashlib.sha256(sys.stdin.buffer.read()).hexdigest())')
expected=$(docker compose -f "$ROOT/docker-compose.yml" exec -T app cat /run/lab/receipt.sha256 | tr -d '\r\n')
if [ "$actual" = "$expected" ]; then
  echo "Correct."
else
  echo "Not yet."
  exit 1
fi
