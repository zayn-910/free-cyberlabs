#!/bin/sh
set -eu

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
LAB="${1:?usage: tools/package-lab.sh <lab-folder> [output-dir]}"
OUT="${2:-$ROOT/dist}"
mkdir -p "$OUT"

python3 - "$LAB" "$OUT" <<'PY'
import pathlib
import sys
import zipfile

lab = pathlib.Path(sys.argv[1]).resolve()
out = pathlib.Path(sys.argv[2]).resolve()
lab_id = ""
for line in (lab / "lab.yml").read_text(encoding="utf-8").splitlines():
    if line.startswith("id:"):
        lab_id = line.split(":", 1)[1].strip().strip('"')
        break
if not lab_id:
    raise SystemExit(f"no id found in {lab}/lab.yml")

target = out / f"{lab_id}.zip"
skip_dirs = {"__pycache__", ".venv", "node_modules"}
skip_suffixes = {".pyc", ".pyo"}
with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
    for path in sorted(lab.rglob("*")):
        if any(part in skip_dirs for part in path.parts):
            continue
        if path.is_file() and path.suffix not in skip_suffixes:
            zf.write(path, pathlib.Path(lab_id) / path.relative_to(lab))
print(target)
PY
