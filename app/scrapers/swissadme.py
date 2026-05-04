from __future__ import annotations

from playwright.sync_api import Browser, sync_playwright


def _swissadme_on_page(page, smiles: str) -> dict:
    page.goto("https://www.swissadme.ch/", wait_until="networkidle", timeout=90_000)
    page.locator("#smiles").fill(smiles)
    page.keyboard.press("Tab")
    page.wait_for_function(
        "() => { const b = document.getElementById('submitButton'); return b && !b.disabled; }",
        timeout=20_000,
    )
    page.evaluate("document.getElementById('submitButton').click()")
    page.wait_for_function(
        "() => document.body.innerText.includes('TPSA') "
        "&& document.body.innerText.includes('Consensus Log P')",
        timeout=120_000,
    )
    return {"html": page.content()}


def run_swissadme(smiles: str, browser: Browser | None = None) -> dict:
    """Fetch SwissADME result HTML for a SMILES string (headless Chromium).

    Wenn ``browser`` gesetzt ist (z. B. gemeinsame Pipeline), wird kein zweites
    ``chromium.launch`` ausgeführt — vermeidet Probleme mit Streamlit/long-lived Prozessen.
    """
    smiles = (smiles or "").strip()
    if browser is not None:
        context = browser.new_context()
        page = context.new_page()
        try:
            return _swissadme_on_page(page, smiles)
        finally:
            context.close()

    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        try:
            context = b.new_context()
            page = context.new_page()
            try:
                return _swissadme_on_page(page, smiles)
            finally:
                context.close()
        finally:
            b.close()
