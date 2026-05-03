from playwright.sync_api import sync_playwright


def run_admetlab(smiles: str):
    """Run single-molecule evaluation on ADMETlab 3.0 and return results HTML."""
    smiles = (smiles or "").strip()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(
            "https://admetlab3.scbdd.com/server/evaluation",
            wait_until="domcontentloaded",
            timeout=90_000,
        )
        page.wait_for_timeout(4000)
        page.locator("input[name=smiles]").wait_for(state="visible", timeout=30_000)
        page.locator("input[name=smiles]").fill(smiles)
        page.get_by_role("button", name="Submit").first.click()
        page.wait_for_url("**/evaluationCal**", timeout=180_000)
        page.wait_for_timeout(3000)
        page.wait_for_function(
            "() => document.body.innerText.includes('logP') "
            "&& document.body.innerText.includes('TPSA')",
            timeout=120_000,
        )
        result_url = page.url
        html = page.content()
        browser.close()
        return {"html": html, "result_url": result_url}
