from playwright.sync_api import sync_playwright


def run_pkcsm(smiles: str):
    """Run pkCSM ADME mode (all pharmacokinetic predictors) and return results HTML."""
    smiles = (smiles or "").strip()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

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
        result_url = page.url
        html = page.content()
        browser.close()
        return {"html": html, "result_url": result_url}
