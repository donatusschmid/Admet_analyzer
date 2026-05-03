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

Öffentlicher Zugriff z. B. mit **Port 8504** und Hostname **`admet.dschmid.cc`**: Eintrag in **`~/.cloudflared/config.yml`** (Ingress auf diesen Port) und passender DNS/CNAME zum laufenden Tunnel — siehe deine zentrale cloudflared-Konfiguration.

## Hinweis

Die Anbindung erfolgt über die öffentlichen Web-Oberflächen der genannten Dienste. Laufzeiten hängen vom Netzwerk ab; Batch-Läufe können pro Struktur mehrere Minuten dauern.
