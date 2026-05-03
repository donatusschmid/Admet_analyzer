# Handbuch für Anwenderinnen und Anwender

Diese Anleitung richtet sich an **Nutzer der Oberfläche**. Technische Details zum Projekt finden Sie in der [README](README.md) und im [technischen Handbuch](USER_MANUAL.md).

---

## Wofür ist das Programm da?

Mit dem **ADMET Multi-Tool Analyzer** können Sie **eine oder viele chemische Strukturen** (als **SMILES**) nacheinander durch **drei kostenlose Webdienste** schicken lassen:

- **SwissADME** – unter anderem Größe, Lipophilie, Oberfläche, einfache Regeln („drug-like“).
- **ADMETlab 3.0** – viele **ADME**- und **Tox**-Vorhersagen.
- **pkCSM** – **Pharmakokinetik** und **Toxizität** (u. a. Aufnahme, Verteilung, Abbau, Ausscheidung).

Die Ergebnisse werden **nebeneinander** dargestellt, damit Sie **vergleichen** können.

**Wichtig:** Das sind durchweg **Computer-Vorhersagen** (in silico), **keine** Laborwerte. Sie eignen sich zum **Einsortieren** und **Vergleichen**, nicht als alleinige Entscheidungsgrundlage.

---

## Programm starten

Wer das Programm **installiert und startet**, braucht dafür die Kurzanleitung in der **README** (Python, Abhängigkeiten, Befehl `streamlit run …`).

**Sie als Anwender** öffnen danach im Browser die angezeigte Adresse (in der Regel eine Seite wie `http://localhost:8501` oder eine von Ihrer IT vorgegebene Adresse).

---

## Die zwei Bereiche (Tabs)

Oben gibt es zwei Register:

1. **Einzelmolekül** – eine Struktur, sofortiger Vergleich der drei Dienste.  
2. **Batch (Datei)** – viele Strukturen aus einer Datei, Ergebnis als Tabelle und **Excel-Datei**.

---

## Einzelmolekül – Schritt für Schritt

1. Geben Sie Ihr **SMILES** in das große Eingabefeld ein (eine Zeile, eine Struktur).  
2. Optional: **„Beispiel: Brigimadlin einsetzen“** lädt ein vorgegebenes Beispiel.  
3. Klicken Sie auf **„Alle drei Tools ausführen“**.  
4. **Warten:** Es kann **einige Minuten** dauern; die drei Webseiten werden nacheinander bedient.  
5. Danach sehen Sie:
   - **Vergleich (Kernparameter)** – die wichtigsten Werte der drei Dienste in einer Tabelle.  
   - Über **„Detail-Parsing pro Tool“** können Sie die ausgelesenen Einzelwerte einsehen.  
   - **Rohdaten** und optional **HTML-Downloads** sind für **tiefere Nachprüfung** gedacht.

**Hinweis:** Die Ergebnisse **bleiben sichtbar**, auch wenn Sie Bereiche auf- und zuklappen – Sie müssen nicht erneut auf „Ausführen“ klicken, solange Sie dieselbe Sitzung nutzen.

**Fehlermeldungen:** Wenn ein Dienst ausfällt oder lange nicht antwortet, kann für diesen Dienst eine **Fehlermeldung** erscheichen; die anderen Spalten können trotzdem gefüllt sein.

---

## Batch (Datei) – Schritt für Schritt

1. Wählen Sie eine Datei: **CSV**, **TXT** oder **SMI** (Textcodierung **UTF-8**).  
2. Legen Sie fest, wie viele Strukturen **höchstens** verarbeitet werden sollen (**Max. Anzahl** – sinnvoll, um sehr lange Läufe zu vermeiden).  
3. Klicken Sie auf **„Batch starten“**.  
4. Der **Fortschrittsbalken** zeigt, welche Struktur gerade dran ist.  
5. Am Ende: **Vorschau** der Tabelle und **„Excel herunterladen“**.

### Was muss in der Datei stehen?

- **CSV:** Eine Spalte mit SMILES – idealerweise mit Überschrift wie `smiles` oder `SMILES`. Fehlt eine solche Überschrift, wird die **erste Spalte** als SMILES gelesen.  
  Optional: eine Spalte mit **Namen oder ID** (z. B. `id`, `name`, `compound_id`), damit die Zeilen in der Auswertung wiedererkennbar sind.  
- **TXT / SMI:** **Pro Zeile ein SMILES.** Leere Zeilen und Zeilen, die mit **#** beginnen, werden ignoriert.

### Zeitplanung

Pro Struktur wird **dieselbe** Abfolge wie im Einzelmodus ausgeführt (alle drei Dienste). **Viele Moleküle** bedeuten **viele Minuten bis Stunden** – nutzen Sie die Begrenzung „Max. Anzahl“, wenn Sie unsicher sind.

---

## Vergleich verstehen (ohne Fachjargon)

- **Molekulargewicht, logP, „polare Oberfläche“** – typische Größen, an denen Sie ähnliche Werkzeuge gewöhnen sind.  
- **Löslichkeit:** Jeder Dienst rechnet **anders**; die Zahlen sind **nicht** 1:1 vergleichbar – eher „grob gleiche Richtung“ beachten.  
- **Aufnahme / Darm / Blut-Hirn-Schranke** – je nach Dienst andere Kennzahl; die Spaltenüberschriften nennen, was gemeint ist.

In der **Excel-Datei** gibt es ein Blatt **Legende** mit kurzen Erklärungen zu den Spalten.

---

## Typische Probleme

| Symptom | Mögliche Ursache |
|--------|-------------------|
| Sehr lange Wartezeit | Normal bei Batch oder langsamer Verbindung; die Webdienste werden live abgefragt. |
| Fehler zu einem der drei Dienste | Internet, Wartung der Webseite oder ungültiges/komplexes SMILES. |
| Leere oder merkwürdige Werte | Grenzen der Vorhersagemodelle; sehr große oder unübliche Moleküle werden von manchen Diensten schlechter unterstützt. |

Bei **Installation, Netzwerk hinter Firma-Firewall oder Cloud-Zugang** wenden Sie sich an die Person, die das Programm bereitstellt.

---

## Datenschutz und Nutzung

- Die Strukturen werden an die **jeweiligen öffentlichen Webangebote** geschickt, so als würden Sie sie dort selbst eingeben.  
- Es gelten die **Nutzungsbedingungen** dieser Anbieter.  
- Nutzen Sie die Vorhersagen **verantwortungsvoll** und nur als **Hilfe**, nicht als alleinige Entscheidungsgrundlage in sensiblen Fragen.

---

*Stand: siehe Versionsverwaltung des Projekts. Bei inhaltlichen Fragen zur Bedienung: siehe [USER_MANUAL.md](USER_MANUAL.md) für ausführlichere technische Erläuterungen.*
