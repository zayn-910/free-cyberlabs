#!/bin/sh
set -eu

cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

docker compose down -v --remove-orphans
docker compose up -d --build --wait
docker compose ps
