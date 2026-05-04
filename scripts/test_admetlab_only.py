#!/usr/bin/env python3
"""Nur ADMETlab 3.0 testen (ohne Streamlit, SwissADME, pkCSM).

Beispiel:
  python scripts/test_admetlab_only.py
  python scripts/test_admetlab_only.py "CC(=O)Oc1ccccc1C(=O)O"

Erreichbarkeit per curl (kein JS, kein Formular):
  curl -sS -o /dev/null -w "HTTP %{http_code}\\n" -L "https://admetlab3.scbdd.com/server/evaluation"
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from app.scrapers.admetlab import run_admetlab  # noqa: E402

_DEFAULT_SMILES = "CC(=O)Oc1ccccc1C(=O)O"  # Aspirin


def main() -> int:
    p = argparse.ArgumentParser(description="Nur ADMETlab-Scraper ausführen.")
    p.add_argument(
        "smiles",
        nargs="?",
        default=_DEFAULT_SMILES,
        help=f"SMILES (Standard: {_DEFAULT_SMILES})",
    )
    args = p.parse_args()
    print("ADMETlab 3.0 (Playwright) …", flush=True)
    out = run_admetlab(args.smiles)
    url = out.get("result_url", "")
    html = out.get("html") or ""
    print(f"OK — result_url: {url}", flush=True)
    print(f"HTML-Länge: {len(html)} Zeichen", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
