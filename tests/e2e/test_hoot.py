from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from tests.e2e.helpers import BASE_URL, login


def test_hoot_suite_succeeds(page: Page) -> None:
    login(page, "admin", "admin")
    page.goto(
        f"{BASE_URL}/web/tests?loglevel=2&preset=desktop&timeout=15000&tag=monodoo",
        wait_until="domcontentloaded",
    )

    # Odoo 19's HOOT UI marks the document title with a check/cross when the
    # runner completes. Keep this bounded so a broken runner cannot make CI
    # appear hung for several minutes.
    try:
        page.wait_for_function(
            "document.title.startsWith('✔') || document.title.startsWith('✖')",
            timeout=60_000,
        )
    except PlaywrightTimeoutError as error:
        status = page.locator(".HootStatusPanel").inner_text(timeout=5_000)
        raise AssertionError(
            f"HOOT did not finish within 60s. title={page.title()!r}; status={status!r}"
        ) from error

    status = page.locator(".HootStatusPanel").inner_text()
    assert "9 tests completed" in status, status
    assert page.title().startswith("✔"), status
