from playwright.sync_api import Page

from tests.e2e.helpers import BASE_URL, login


def test_hoot_suite_succeeds(page: Page) -> None:
    login(page, "admin", "admin")
    page.goto(
        f"{BASE_URL}/web/tests?loglevel=2&preset=desktop&timeout=15000&tag=monodoo",
        wait_until="domcontentloaded",
    )

    # Odoo 19's HOOT UI marks the document title with a check/cross when the
    # runner completes.  This is more reliable in Playwright than scraping
    # console output, which is primarily consumed by Odoo's own browser_js
    # harness.
    page.wait_for_function(
        "document.title.startsWith('✔') || document.title.startsWith('✖')",
        timeout=300_000,
    )

    status = page.locator(".HootStatusPanel").inner_text()
    assert "9 tests completed" in status, status
    assert page.title().startswith("✔"), status
