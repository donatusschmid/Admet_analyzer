# Admet_analyzer – User Manual

**Rein anwenderorientiert (ohne technische Projekt-Details):** [ANWENDERHANDBUCH.md](ANWENDERHANDBUCH.md)

## 1. Zweck

**Admet_analyzer** ist eine **Streamlit-Webanwendung**, die für eine oder mehrere **SMILES**-Strukturen nacheinander drei öffentliche Webdienste aufruft:

| Dienst | Inhalt (Kurz) |
|--------|----------------|
| **SwissADME** | Physiko-chemische Eigenschaften, Drug-Likeness, u. a. |
| **ADMETlab 3.0** | Viele ADME- und Tox-Endpunkte |
| **pkCSM** | Pharmakokinetik und Toxizität (u. a. ADME-Modus) |

Die App **steuert die Browser-Oberflächen** (Playwright), liest die Ergebnisse ein und stellt einen **Vergleich** der wichtigsten Kennzahlen dar. Es handelt sich durchgängig um **in-silico-Vorhersagen**, keine Laborwerte.

---

## 2. Voraussetzungen

- **Python** 3.10 oder neuer
- **Internetzugang** (Zugriff auf die drei Websites)
- **Playwright Chromium** (nach Installation einmal `playwright install chromium`)
- Ausreichend **RAM/CPU**; ein vollständiger Drei-Tool-Lauf kann **mehrere Minuten** dauern

---

## 3. Installation

Im **Projektroot** (Ordner mit `app/` und `requirements.txt`):

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

---

## 4. Programm starten

```bash
streamlit run app/main.py
```

Standard öffnet Streamlit meist **http://localhost:8501** (Port kann abweichen).

**Fester Port** (z. B. für Reverse Proxy / Cloudflare):

```bash
streamlit run app/main.py --server.port 8504 --server.address 127.0.0.1
```

---

## 5. Oberfläche – Tab „Einzelmolekül“

1. **SMILES eingeben** im Textfeld (eine Struktur pro Lauf).
2. Optional: **„Beispiel: Brigimadlin einsetzen“** – füllt ein vordefiniertes SMILES ein.
3. **„Alle drei Tools ausführen“** startet nacheinander SwissADME → ADMETlab → pkCSM.
4. Nach Abschluss erscheinen u. a.:
   - **Vergleich (Kernparameter)** – Tabelle (Endpunkte × drei Dienste).
   - **Detail-Parsing** (Expander) – extrahierte Rohfelder pro Tool.
   - **Rohdaten** – Metadaten; HTML nur als Größe/Zusammenfassung.
   - **Vollständiges Roh-HTML** (Expander) – **Download** pro Tool als `.html`.

**Hinweis:** Ergebnisse bleiben in der Session sichtbar, auch wenn du Expander öffnest (erneuter Seitenaufbau ohne erneuten Klick auf „Ausführen“).

**Fehler:** Wenn einzelne Tools fehlschlagen, erscheinen **Warnungen/Fehler** mit Kurztext; die Tabelle kann dann Lücken haben.

---

## 6. Oberfläche – Tab „Batch (Datei)“

1. **SMILES-Datei** hochladen: **CSV**, **TXT** oder **SMI** (UTF-8).
2. **Max. Anzahl Strukturen** (1–200, Standard 20) begrenzt die abgearbeiteten Zeilen.
3. **„Batch starten“** – nur aktiv, wenn eine Datei gewählt ist.

### Dateiformate

- **CSV:** Spalte **`smiles`**, **`SMILES`**, **`smile`** oder **`canonical_smiles`**; fehlt diese, wird die **erste Spalte** als SMILES verwendet.  
  Optional: **`id`**, **`name`**, **`compound_id`**, **`compound`**, **`mol`**, **`identifier`** für die Anzeige-ID.
- **TXT / SMI:** **Eine SMILES pro Zeile**; leere Zeilen und Zeilen, die mit **`#`** beginnen, werden ignoriert.

### Ablauf und Ergebnis

- Pro Zeile wird **dieselbe Pipeline** wie im Einzeltab ausgeführt (alle drei Tools nacheinander).
- **Fortschrittsbalken** zeigt den aktuellen Eintrag.
- Nach Abschluss: **Vorschau-Tabelle** und **„Excel herunterladen (.xlsx)“**.

Die Excel-Datei enthält u. a. Blätter **Ergebnisse** (formatiert) und **Legende** (Spaltenbedeutung).

**Wichtig:** Batch-Zeit ≈ **Anzahl Strukturen × (Zeit eines vollen Drei-Tool-Laufs)** – bei vielen Molekülen sehr lang.

---

## 7. Verglichene Kennzahlen (Überblick)

Die App bündelt u. a. (je nach Verfügbarkeit im HTML):

- Molekulargewicht
- logP
- TPSA (pkCSM liefert ggf. „Surface Area“ mit Hinweis, nicht identisch mit TPSA)
- Löslichkeit (tool-spezifische Skalen – **nicht** ohne Weiteres vergleichbar)
- Resorption / HIA / intestinale Aufnahme (je nach Tool)
- Caco-2, BBB (wo vorhanden)

Genau Spaltennamen und Fehler-Spalten siehe Excel-Legende bzw. Batch-Tabelle.

---

## 8. Öffentlicher Zugriff (optional, Cloudflare)

Wenn du z. B. **`admet.dschmid.cc`** nutzt: In **`~/.cloudflared/config.yml`** muss für den laufenden Tunnel ein **`ingress`**-Eintrag **`hostname: admet.dschmid.cc`** auf **`http://127.0.0.1:8504`** (oder deinen Streamlit-Port) zeigen, und Streamlit muss auf diesem Port laufen.

**HTTP 404 im Browser:** Häufig **mehrere** `cloudflared`-Instanzen oder ein Tunnel **ohne** passenden `ingress` für diese Domain. Nur **eine** saubere Tunnel-Konfiguration pro Hostname verwenden; siehe auch **README.md** im Repo.

---

## 9. Einschränkungen und Hinweise

- **Websites können sich ändern** – Selektoren/Wartezeiten in den Scrapern ggf. anpassen.
- **ADMETlab** empfiehlt u. a. keine sehr großen Moleküle (>128 Atome); andere Grenzen je nach Dienst.
- **Nutzungsbedingungen** der drei Dienste sind durch dich einzuhalten; die App automatisiert nur die öffentliche Oberfläche.
- **Keine Garantie** für Vollständigkeit oder medizinische Aussagen – nur Screening-Hilfe.

---

## 10. Technische Struktur (Kurz)

| Pfad | Rolle |
|------|--------|
| `app/main.py` | Streamlit-UI |
| `app/services/aggregator.py` | Orchestrierung der drei Tools |
| `app/scrapers/` | Playwright-Zugriffe auf die Webseiten |
| `app/parsers/` | HTML → strukturierte Felder |
| `app/services/smiles_file.py` | Batch-Datei einlesen |
| `app/services/excel_export.py` | Excel-Export |

---

## 11. Weitere Dokumentation

- **README.md** – Installation, Start, Kurz-Hinweise zu Cloudflare  
- **ANWENDERHANDBUCH.md** – Bedienung für Endnutzer ohne Technik-Hintergrund
