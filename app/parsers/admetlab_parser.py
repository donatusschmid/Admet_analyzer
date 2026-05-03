from bs4 import BeautifulSoup


def _table_kv_map(html: str) -> dict[str, str]:
    soup = BeautifulSoup(html, "lxml")
    out: dict[str, str] = {}
    for row in soup.find_all("tr"):
        cols = [c.get_text(" ", strip=True) for c in row.find_all(["td", "th"])]
        if len(cols) >= 2 and cols[0] and cols[1]:
            out[cols[0]] = cols[1]
    return out


def parse_admetlab(html: str) -> dict:
    m = _table_kv_map(html)
    kl = {k.lower(): (k, v) for k, v in m.items()}

    def pick(*substrings: str) -> str | None:
        for s in substrings:
            for key, (orig, val) in kl.items():
                if s in key:
                    return val
        return None

    return {
        "MW": pick("molecular weight (mw)", "molecular weight"),
        "TPSA": m.get("TPSA") or pick("tpsa"),
        "logP": m.get("logP") or pick("logp"),
        "logS": m.get("logS") or pick("logs"),
        "Caco2": pick("caco-2 permeability", "caco-2"),
        "HIA": m.get("HIA") or pick("hia"),
    }
