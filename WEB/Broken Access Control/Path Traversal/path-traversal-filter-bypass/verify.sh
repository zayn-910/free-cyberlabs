#!/bin/sh
set -e

if [ $# -ne 1 ]; then
  echo "Usage: ./verify.sh 'FLAG{...}'"
  exit 2
fi

SUBMITTED_HASH=$(printf '%s' "$1" | sha256sum | cut -d' ' -f1)
REAL_HASH=$(docker compose exec -T app cat /app/flag.sha256 | tr -d '\r\n')

if [ "$SUBMITTED_HASH" = "$REAL_HASH" ]; then
  echo "✓ Correct! Well done."
else
  echo "✗ Not quite. Keep trying."
  exit 1
fi
