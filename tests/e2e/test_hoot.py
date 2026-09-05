from playwright.sync_api import Page

from tests.e2e.helpers import BASE_URL, login


def test_hoot_suite_succeeds(page: Page) -> None:
    login(page, "admin", "admin")
    hoot_failures: list[str] = []
    page.on(
        "console",
        lambda message: hoot_failures.append(message.text)
        if "[HOOT]" in message.text and "failed" in message.text.lower()
        else None,
    )
    with page.expect_console_message(
        predicate=lambda message: "[HOOT] Test suite succeeded" in message.text,
        timeout=3_600_000,
    ):
        page.goto(
            f"{BASE_URL}/web/tests?headless&loglevel=2&preset=desktop&timeout=15000",
            wait_until="domcontentloaded",
        )
    assert not hoot_failures
