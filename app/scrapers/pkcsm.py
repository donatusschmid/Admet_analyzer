from __future__ import annotations

from playwright.sync_api import Browser, sync_playwright


def _pkcsm_on_page(page, smiles: str) -> dict:
    page.goto(
        "https://biosig.lab.uq.edu.au/pkcsm/prediction",
        wait_until="domcontentloaded",
        timeout=90_000,
    )
    page.wait_for_timeout(5000)
    page.locator("input[name=smiles_str]").wait_for(state="visible", timeout=30_000)
    page.locator("input[name=smiles_str]").fill(smiles)
    page.locator('button[name=pred_type][value=adme]').click()
    page.wait_for_url("**/prediction_single/**", timeout=180_000)
    page.wait_for_timeout(2000)
    page.wait_for_function(
        """() => {
          const t = document.body.innerText;
          const i = t.indexOf('Property');
          if (i < 0) return false;
          return !t.slice(i).includes('Running');
        }""",
        timeout=300_000,
    )
    page.wait_for_timeout(800)
    return {"html": page.content(), "result_url": page.url}


def run_pkcsm(smiles: str, browser: Browser | None = None) -> dict:
    """Run pkCSM ADME mode and return results HTML.

    Optional shared ``browser`` für die Multi-Tool-Pipeline (ein Launch pro Lauf).
    """
    smiles = (smiles or "").strip()
    if browser is not None:
        context = browser.new_context()
        page = context.new_page()
        try:
            return _pkcsm_on_page(page, smiles)
        finally:
            context.close()

    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        try:
            context = b.new_context()
            page = context.new_page()
            try:
                return _pkcsm_on_page(page, smiles)
            finally:
                context.close()
        finally:
            b.close()
