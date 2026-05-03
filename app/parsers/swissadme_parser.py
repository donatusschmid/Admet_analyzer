from bs4 import BeautifulSoup


def parse_swissadme(html: str):
    soup = BeautifulSoup(html, "lxml")
    data = {}

    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cols = [c.get_text(" ", strip=True) for c in row.find_all("td")]
            if len(cols) < 2:
                continue
            key, value = cols[0], cols[1]
            kl = key.lower()

            if "topological polar surface area" in kl or (
                key.strip().startswith("TPSA") and "polar" in kl
            ):
                data["TPSA"] = value

            if "consensus log p" in kl and "average" in kl:
                data["logP"] = value

            if kl.startswith("molecular weight") or kl.startswith("molecular mass"):
                data["MW"] = value

            if "log s (esol)" in kl or kl.startswith("log s (esol)"):
                data["logS_ESOL"] = value

            if "gi absorption" in kl or "gatrointestinal absorption" in kl:
                data["GI_absorption"] = value

    return data
