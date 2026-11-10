#!/bin/sh
set -eu

APP_DIR="${PORTAL_APP_DIR:-/app}"
cd "$APP_DIR"
exec python seed_data.py
