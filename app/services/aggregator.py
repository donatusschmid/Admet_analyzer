from collections.abc import Callable

from playwright.sync_api import sync_playwright

from app.parsers.admetlab_parser import parse_admetlab
from app.parsers.pkcsm_parser import parse_pkcsm
from app.parsers.swissadme_parser import parse_swissadme
from app.scrapers.admetlab import run_admetlab
from app.scrapers.pkcsm import run_pkcsm
from app.scrapers.swissadme import run_swissadme


def _safe_call(name: str, fn, smiles: str):
    try:
        return None, fn(smiles)
    except Exception as e:
        return f"{name}: {e}", None


def run_pipeline(
    smiles: str,
    on_progress: Callable[[float, str], None] | None = None,
):
    """Run SwissADME, ADMETlab 3.0, and pkCSM; parse and align key endpoints.

    Ein gemeinsames Chromium pro Lauf (kein dreifaches ``launch``) — vermeidet Fehler,
    wenn die App in einem lang laufenden Prozess (z. B. Streamlit) mehrere Playwright-
    Sitzungen nacheinander startet.

    ``on_progress(anteil, nachricht)``: ``anteil`` in [0, 1] für UI-Fortschritt.
    """
    smiles = (smiles or "").strip()
    raw_results: dict = {}
    errors: dict[str, str] = {}
    swiss_raw: dict = {}
    admet_raw: dict = {}
    pk_raw: dict = {}

    def _p(frac: float, msg: str) -> None:
        if on_progress:
            on_progress(min(1.0, max(0.0, frac)), msg)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:

            def _swiss(s: str):
                return run_swissadme(s, browser=browser)

            def _admet(s: str):
                return run_admetlab(s, browser=browser)

            def _pk(s: str):
                return run_pkcsm(s, browser=browser)

            _p(0.0, "1/5 SwissADME — Seite abrufen und auswerten …")
            err, swiss_raw = _safe_call("SwissADME", _swiss, smiles)
            if err:
                errors["swissadme"] = err
                swiss_raw = {}
            raw_results["swissadme"] = swiss_raw

            _p(0.22, "2/5 ADMETlab 3.0 — Seite abrufen und auswerten …")
            err, admet_raw = _safe_call("ADMETlab 3.0", _admet, smiles)
            if err:
                errors["admetlab"] = err
                admet_raw = {}
            raw_results["admetlab"] = admet_raw

            _p(0.44, "3/5 pkCSM — Seite abrufen und auswerten …")
            err, pk_raw = _safe_call("pkCSM", _pk, smiles)
            if err:
                errors["pkcsm"] = err
                pk_raw = {}
            raw_results["pkcsm"] = pk_raw
        finally:
            browser.close()

    _p(0.66, "4/5 Rohdaten parsen und Vergleich bilden …")
    swiss = parse_swissadme(swiss_raw.get("html", ""))
    admet = parse_admetlab(admet_raw.get("html", ""))
    pk = parse_pkcsm(pk_raw.get("html", ""))

    pk_sa = pk.get("SurfaceArea")
    tpsa_pkcsm = f"{pk_sa} (pkCSM surface area, not TPSA)" if pk_sa else None

    comparison = {
        "Molecular weight": {
            "SwissADME": swiss.get("MW"),
            "ADMETlab 3.0": admet.get("MW"),
            "pkCSM": pk.get("MW"),
        },
        "logP": {
            "SwissADME": swiss.get("logP"),
            "ADMETlab 3.0": admet.get("logP"),
            "pkCSM": pk.get("LogP"),
        },
        "TPSA (Å²)": {
            "SwissADME": swiss.get("TPSA"),
            "ADMETlab 3.0": admet.get("TPSA"),
            "pkCSM": tpsa_pkcsm,
        },
        "Aqueous solubility (tool-specific)": {
            "SwissADME": swiss.get("logS_ESOL"),
            "ADMETlab 3.0": admet.get("logS"),
            "pkCSM": pk.get("WaterSolubility"),
        },
        "GI absorption (Swiss) / HIA (ADMETlab) / Intestinal % (pkCSM)": {
            "SwissADME": swiss.get("GI_absorption"),
            "ADMETlab 3.0": admet.get("HIA"),
            "pkCSM": pk.get("IntestinalAbsorption"),
        },
        "Caco-2 permeability (log Papp)": {
            "SwissADME": None,
            "ADMETlab 3.0": admet.get("Caco2"),
            "pkCSM": pk.get("Caco2"),
        },
        "BBB permeability (pkCSM)": {
            "SwissADME": None,
            "ADMETlab 3.0": None,
            "pkCSM": pk.get("BBB"),
        },
    }

    parsed_by_tool = {
        "swissadme": swiss,
        "admetlab": admet,
        "pkcsm": pk,
    }

    _p(1.0, "5/5 Fertig.")

    return {
        "raw": raw_results,
        "normalized": comparison,
        "parsed": parsed_by_tool,
        "errors": errors,
    }
