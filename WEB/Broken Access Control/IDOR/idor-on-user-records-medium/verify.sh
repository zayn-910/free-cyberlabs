#!/bin/sh
set -u

cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)" || exit 2

if [ "$#" -ne 1 ]; then
  echo "usage: ./verify.sh <recovered-value>" >&2
  exit 2
fi

# Accept a value copied with surrounding whitespace or pasted inside a line
# of text; the recovered value itself is still compared exactly.
SUBMITTED="$(printf '%s' "$1" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
EXTRACTED="$(printf '%s' "$SUBMITTED" | grep -oE 'FLAG\{[0-9A-Fa-f]{32}\}' | head -n 1 || true)"
if [ -n "$EXTRACTED" ]; then
  SUBMITTED="$EXTRACTED"
fi

CANDIDATE_HASH="$(printf '%s\n' "$SUBMITTED" | sha256sum | cut -d ' ' -f 1)"

if ! STORED_HASH="$(docker compose exec -T app cat /data/runtime/flag.sha256)"; then
  echo "The portal is not reachable through Docker Compose. Start it with: docker compose up -d --build" >&2
  echo "Compose status:" >&2
  docker compose ps >&2 || true
  exit 2
fi
STORED_HASH="$(printf '%s' "$STORED_HASH" | tr -d '\r\n ')"

if ! RUNTIME_HASH="$(docker compose exec -T app sha256sum /data/runtime/flag)"; then
  echo "The portal is not reachable through Docker Compose. Start it with: docker compose up -d --build" >&2
  echo "Compose status:" >&2
  docker compose ps >&2 || true
  exit 2
fi
RUNTIME_HASH="$(printf '%s' "$RUNTIME_HASH" | cut -d ' ' -f 1)"

if [ -z "$STORED_HASH" ] || [ "$STORED_HASH" != "$RUNTIME_HASH" ]; then
  echo "The lab state is inconsistent. Recreate it with: docker compose up -d --force-recreate" >&2
  exit 2
fi

if [ "$CANDIDATE_HASH" = "$STORED_HASH" ]; then
  echo "Correct."
  exit 0
fi

echo "Not yet."
exit 1
