# Remote-Zugriff: `admet.dschmid.cc` → Streamlit (Port 8504)

Die Domain **dschmid.cc** muss bei Cloudflare liegen (Nameserver). Der Tunnel verbindet **admet.dschmid.cc** mit deinem lokalen Streamlit auf **127.0.0.1:8504**.

## 1. Einmalig: Login & Tunnel anlegen

```bash
cloudflared tunnel login
# Browser öffnet sich – Zone wählen, die dschmid.cc enthält.

cloudflared tunnel create admet-analyzer
```

Notiere **Tunnel-ID** und den Pfad zur **credentials-JSON** (meist `~/.cloudflared/<UUID>.json`).

## 2. DNS-Eintrag (CNAME) anlegen

Das legt automatisch den DNS-Eintrag in Cloudflare an (kein manueller A-Record nötig). **Option `-f` muss vor Tunnel-Name und Hostname stehen**, wenn ein Eintrag überschrieben werden soll:

```bash
cloudflared tunnel route dns -f admet-analyzer admet.dschmid.cc
```

### Hostname hing noch an einem anderen Tunnel?

Wenn die Meldung einen **anderen** `tunnelID` nennt (z. B. `vkm-agent`):

1. **Zero Trust** → **Networks** → **Tunnels** → den alten Tunnel öffnen → unter **Public hostnames** den Eintrag für `admet.dschmid.cc` **löschen**.
2. Optional **DNS** → Datensatz **admet** (CNAME) löschen.
3. Erneut ausführen:

```bash
cloudflared tunnel route dns -f admet-analyzer admet.dschmid.cc
```

Ziel im DNS: CNAME auf `<tunnel-id-admet-analyzer>.cfargotunnel.com`.

### Bereits angelegter Tunnel in diesem Projekt

Tunnel-Name: **`admet-analyzer`**, ID: **`c0af0e81-a06e-4735-8339-8be7e87dd1ad`**, Credentials:  
`~/.cloudflared/c0af0e81-a06e-4735-8339-8be7e87dd1ad.json`

Lokale Datei **`cloudflared/config.yml`** (nicht im Git) ist dafür vorkonfiguriert — bitte DNS wie oben auf diesen Tunnel umhängen, falls noch `vkm-agent` aktiv war.

## 3. Konfiguration im Projekt

**Richtige Datei:** `admet-streamlit-analyzer/cloudflared/config.yml` (im Repo-Ordner, **nicht** automatisch `~/.cloudflared/config.yml`).

Der Hostname **`admet.dschmid.cc`** steht dort unter **`ingress:`** als `hostname:` (siehe auch `config.example.yml`).

```bash
cd /pfad/zu/admet-streamlit-analyzer/cloudflared
cp config.example.yml config.yml
```

In `config.yml` eintragen:

- `tunnel:` → deine **Tunnel-UUID** (aus `cloudflared tunnel list`)
- `credentials-file:` → voller Pfad zur `.json` (wie von `tunnel create` ausgegeben)

`config.yml` ist in `.gitignore` und wird nicht ins Repo committet.

## 4. Streamlit auf Port 8504 starten

```bash
cd /pfad/zu/admet-streamlit-analyzer
source .venv/bin/activate
streamlit run app/main.py --server.port 8504 --server.address 127.0.0.1
```

`127.0.0.1` reicht, weil nur cloudflared auf dem Rechner zugreift.

## 5. Tunnel starten

```bash
./scripts/run-cloudflared.sh
# oder:
cloudflared tunnel --config cloudflared/config.yml run
```

Beide Prozesse laufen lassen (Streamlit + cloudflared). Danach: **https://admet.dschmid.cc**

## Fehlersuche

- **502 / Error 1033:** Streamlit läuft nicht oder nicht auf 8504.
- **DNS:** Einige Minuten warten nach `tunnel route dns`; Cache leeren.
- **Tunnel:** `cloudflared tunnel list` / `cloudflared tunnel info admet-analyzer`
