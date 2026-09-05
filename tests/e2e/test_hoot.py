from playwright.sync_api import Page

from tests.e2e.helpers import BASE_URL, login


def hoot_hash(test_string: str) -> str:
    """Match Odoo 19 HOOT's 32-bit descriptor hash used by /web/tests?id=."""
    value = 0
    for char in test_string:
        value = ((value << 5) - value + ord(char)) & 0xFFFFFFFF
    return f"{value:08x}"


def test_hoot_suite_succeeds(page: Page) -> None:
    login(page, "admin", "admin")
    hoot_failures: list[str] = []
    page.on(
        "console",
        lambda message: hoot_failures.append(message.text)
        if "[HOOT]" in message.text and "failed" in message.text.lower()
        else None,
    )
    monodoo_suite = hoot_hash("@monodoo_home")
    with page.expect_console_message(
        predicate=lambda message: "[HOOT] Test suite succeeded" in message.text,
        timeout=300_000,
    ):
        page.goto(
            f"{BASE_URL}/web/tests?headless&loglevel=2&preset=desktop&timeout=15000&id={monodoo_suite}",
            wait_until="domcontentloaded",
        )
    assert not hoot_failures
