#!/bin/sh
set -e

if docker compose ps --format '{{.State}}' 2>/dev/null | grep -q running; then
  echo "Regenerating flag..."
  docker compose exec -T app sh -c '
    rm -f /app/flag.txt /app/flag.sha256
    umask 077
    RAW=$(openssl rand -hex 16)
    printf "FLAG{%s}" "$RAW" > /app/flag.txt
    sha256sum /app/flag.txt | cut -d" " -f1 > /app/flag.sha256
  '
  echo "Done. A new flag has been generated."
else
  echo "Lab is not running. Starting fresh..."
  docker compose down -v 2>/dev/null || true
  docker compose up -d --build
  echo "Done. Lab started with a new flag."
fi
