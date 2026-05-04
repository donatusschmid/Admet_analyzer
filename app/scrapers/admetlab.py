from __future__ import annotations

import re

from playwright.sync_api import Browser, sync_playwright

# ADMETlab-Auswertung kann bei Auslastung oder großen Molekülen sehr lange brauchen.
_DEFAULT_MS = 300_000  # 5 Min Standard für Aktionen / Navigation
_GOTO_MS = 240_000
_WAIT_RESULTS_MS = 420_000  # 7 Min bis Ergebnis-URL + Tabelleninhalt
# SPA / langsame Verbindung: Eingabefeld kann Minuten brauchen; nicht an Pixel-Sichtbarkeit festhalten.
_WAIT_FORM_MS = 600_000  # 10 Min


def _wait_smiles_input_in_dom(page):
    """Wartet, bis ein SMILES-Feld im DOM existiert (lockerer als reine Sichtbarkeit)."""
    page.wait_for_function(
        """() => {
          return !!(
            document.querySelector('input[name="smiles"]') ||
            document.querySelector('input#smiles') ||
            document.querySelector('textarea[name="smiles"]') ||
            document.querySelector('input[type="text"][name="smiles"]')
          );
        }""",
        timeout=_WAIT_FORM_MS,
    )


def _fill_smiles(page, smiles: str):
    locators = [
        page.locator('input[name="smiles"]'),
        page.locator("input#smiles"),
        page.locator('textarea[name="smiles"]'),
    ]
    last_err = None
    for loc in locators:
        try:
            if loc.count() == 0:
                continue
            first = loc.first
            first.wait_for(state="attached", timeout=60_000)
            try:
                first.fill(smiles, timeout=_DEFAULT_MS)
            except Exception:
                first.fill(smiles, timeout=_DEFAULT_MS, force=True)
            return
        except Exception as e:
            last_err = e
    raise last_err or RuntimeError("Kein SMILES-Eingabefeld auf ADMETlab gefunden.")


def _click_evaluation_submit(page):
    """Mehrere „Submit“-Buttons; den letzten sichtbaren bevorzugen (Hauptformular)."""
    role_btns = page.get_by_role("button", name=re.compile(r"submit", re.I))
    n = role_btns.count()
    for i in range(n - 1, -1, -1):
        btn = role_btns.nth(i)
        try:
            if btn.is_visible():
                btn.click(timeout=_DEFAULT_MS)
                return
        except Exception:
            continue
    fallback = page.locator("button").filter(has_text=re.compile(r"submit", re.I))
    fc = fallback.count()
    for i in range(fc - 1, -1, -1):
        btn = fallback.nth(i)
        if btn.is_visible():
            btn.click(timeout=_DEFAULT_MS)
            return
    raise RuntimeError("Kein sichtbarer Submit-Button auf ADMETlab gefunden.")


def _admetlab_on_page(page, smiles: str) -> dict:
    page.set_default_timeout(_DEFAULT_MS)
    page.set_default_navigation_timeout(_DEFAULT_MS)

    page.goto(
        "https://admetlab3.scbdd.com/server/evaluation",
        wait_until="domcontentloaded",
        timeout=_GOTO_MS,
    )
    try:
        page.wait_for_load_state("load", timeout=60_000)
    except Exception:
        pass
    page.wait_for_timeout(3000)
    _wait_smiles_input_in_dom(page)
    _fill_smiles(page, smiles)
    _click_evaluation_submit(page)
    page.wait_for_url("**/evaluationCal**", timeout=_WAIT_RESULTS_MS)
    page.wait_for_timeout(5000)
    page.wait_for_function(
        "() => document.body.innerText.includes('logP') "
        "&& document.body.innerText.includes('TPSA')",
        timeout=_WAIT_RESULTS_MS,
    )
    return {"html": page.content(), "result_url": page.url}


def run_admetlab(smiles: str, browser: Browser | None = None) -> dict:
    """Run single-molecule evaluation on ADMETlab 3.0 and return results HTML.

    Mit gemeinsamem ``browser`` (Pipeline) nur ein Chromium-Launch — wichtig für Streamlit.
    """
    smiles = (smiles or "").strip()
    if browser is not None:
        context = browser.new_context()
        page = context.new_page()
        try:
            return _admetlab_on_page(page, smiles)
        finally:
            context.close()

    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        try:
            context = b.new_context()
            page = context.new_page()
            try:
                return _admetlab_on_page(page, smiles)
            finally:
                context.close()
        finally:
            b.close()
