# Admet_analyzer

Streamlit-App zum Vergleich von **SwissADME**, **ADMETlab 3.0** und **pkCSM** für einzelne SMILES oder per Batch (CSV/TXT). Ergebnisse optional als formatierte Excel-Datei.

Ausführliches **Bedienungshandbuch:** [USER_MANUAL.md](USER_MANUAL.md).

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

Öffentlicher Zugriff z. B. mit **Port 8504** und Hostname **`admet.dschmid.cc`**: In **`~/.cloudflared/config.yml`** (Tunnel **vkm-agent**) muss unter `ingress` eine Zeile `hostname: admet.dschmid.cc` → `service: http://127.0.0.1:8504` stehen. Streamlit dann mit `--server.port 8504` starten.

**HTTP 404 im Browser:** Häufig laufen **zwei** cloudflared-Instanzen (z. B. **vkm-agent** und **admet-analyzer**). **`admet.dschmid.cc`** wird dann an den Tunnel **ohne** Eintrag für diese Domain geroutet → 404. **Lösung:** Alle `cloudflared`-Prozesse beenden, nur **eine** Instanz starten: **`cloudflared tunnel run`** (liest `~/.cloudflared/config.yml` mit **vkm-agent** und dem `admet`-Ingress). Wenn du **admet-analyzer** nicht brauchst: Prozess dauerhaft stoppen, optional `cloudflared tunnel delete admet-analyzer` (nur wenn keine aktiven Verbindungen). Brauchst du zwei Tunnel, muss **jeder** eine eigene Config mit passendem `tunnel:` und `ingress` für seine Hostnames haben — nicht `tunnel run admet-analyzer` neben einer `config.yml`, die nur **vkm-agent** beschreibt.

## Hinweis

Die Anbindung erfolgt über die öffentlichen Web-Oberflächen der genannten Dienste. Laufzeiten hängen vom Netzwerk ab; Batch-Läufe können pro Struktur mehrere Minuten dauern.
