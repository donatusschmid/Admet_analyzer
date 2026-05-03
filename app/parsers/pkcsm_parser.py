import re

from bs4 import BeautifulSoup


def parse_pkcsm(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    data: dict[str, str | None] = {
        "MW": None,
        "LogP": None,
        "SurfaceArea": None,
        "WaterSolubility": None,
        "IntestinalAbsorption": None,
        "Caco2": None,
        "BBB": None,
    }

    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        if not rows:
            continue
        header_cells = [c.get_text(" ", strip=True) for c in rows[0].find_all(["th", "td"])]
        if header_cells[:2] == ["Descriptor", "Value"]:
            for row in rows[1:]:
                cols = [c.get_text(" ", strip=True) for c in row.find_all(["td", "th"])]
                if len(cols) < 2:
                    continue
                key, val = cols[0], cols[1]
                lk = key.lower()
                if lk == "molecular weight":
                    data["MW"] = val
                elif lk == "logp":
                    data["LogP"] = val
                elif "surface area" in lk:
                    data["SurfaceArea"] = val
            continue

        if len(header_cells) >= 3 and "Predicted Value" in header_cells:
            hmap = {name: i for i, name in enumerate(header_cells)}
            pi = hmap.get("Predicted Value")
            prop_i = hmap.get("Property")
            model_i = hmap.get("Model Name")
            if pi is None or prop_i is None:
                continue
            for row in rows[1:]:
                cols = [c.get_text(" ", strip=True) for c in row.find_all("td")]
                if len(cols) <= pi:
                    continue
                prop = cols[prop_i]
                model = cols[model_i] if model_i is not None and model_i < len(cols) else ""
                val = cols[pi]
                if "Water solubility" in model:
                    data["WaterSolubility"] = val
                elif "Intestinal absorption" in model:
                    data["IntestinalAbsorption"] = val
                elif "Caco2" in model or "Caco-2" in model:
                    data["Caco2"] = val
                elif prop == "Distribution" and "BBB permeability" in model:
                    data["BBB"] = val

    text = soup.get_text("\n", strip=True)
    if data["WaterSolubility"] is None:
        m = re.search(
            r"Water solubility\t([^\t\n]+)",
            text,
            re.I,
        )
        if m:
            data["WaterSolubility"] = m.group(1).strip()

    return {k: v for k, v in data.items() if v is not None}
