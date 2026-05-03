from playwright.sync_api import sync_playwright


def run_swissadme(smiles: str):
    """Fetch SwissADME result HTML for a SMILES string (headless Chromium)."""
    smiles = (smiles or "").strip()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

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
        html = page.content()

        browser.close()

        return {"html": html}
