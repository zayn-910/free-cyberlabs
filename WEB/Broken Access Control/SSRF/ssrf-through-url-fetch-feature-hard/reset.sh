#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
docker compose -f "$ROOT/docker-compose.yml" down --volumes --remove-orphans
docker compose -f "$ROOT/docker-compose.yml" up -d --build --wait
