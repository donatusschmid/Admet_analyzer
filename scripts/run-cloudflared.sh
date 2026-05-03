#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CFG="$ROOT/cloudflared/config.yml"
if [[ ! -f "$CFG" ]]; then
  echo "Fehlt: $CFG"
  echo "Siehe cloudflared/README.md — config.example.yml nach config.yml kopieren und ausfüllen."
  exit 1
fi
exec cloudflared tunnel --config "$CFG" run
