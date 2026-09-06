from playwright.sync_api import Page

from tests.e2e.helpers import BASE_URL, login


def test_hoot_suite_succeeds(page: Page) -> None:
    login(page, "admin", "admin")
    hoot_messages: list[str] = []

    def collect_hoot_message(message) -> None:
        if "[HOOT]" in message.text:
            hoot_messages.append(message.text)

    page.on("console", collect_hoot_message)
    with page.expect_console_message(
        predicate=lambda message: "[HOOT]" in message.text
        and (
            "Test suite succeeded" in message.text
            or "failed" in message.text.lower()
        ),
        timeout=300_000,
    ) as terminal_message:
        page.goto(
            f"{BASE_URL}/web/tests?headless&loglevel=2&preset=desktop&timeout=15000&tag=monodoo",
            wait_until="domcontentloaded",
        )

    result = terminal_message.value.text
    assert "Test suite succeeded" in result, "\n".join(hoot_messages)
