# Admet_analyzer

Streamlit-App zum Vergleich von **SwissADME**, **ADMETlab 3.0** und **pkCSM** für einzelne SMILES oder per Batch (CSV/TXT). Ergebnisse optional als formatierte Excel-Datei.

## Voraussetzungen

- Python 3.10+
- Chromium für Playwright (wird mit `playwright install` eingerichtet)

## Installation

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

## Start

```bash
streamlit run app/main.py
```

Im Projektroot ausführen.

## Hinweis

Die Anbindung erfolgt über die öffentlichen Web-Oberflächen der genannten Dienste. Laufzeiten hängen vom Netzwerk ab; Batch-Läufe können pro Struktur mehrere Minuten dauern.
