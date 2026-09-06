from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from tests.e2e.helpers import BASE_URL, login


def test_hoot_suite_succeeds(page: Page) -> None:
    login(page, "admin", "admin")

    messages: list[str] = []
    page.on("console", lambda message: messages.append(message.text))

    # Odoo 19's own HOOT browser tests use the `headless` query flag and wait
    # for the runner's console success signal. Without `headless`, /web/tests
    # intentionally remains in the interactive `Ready` state until started by
    # a user, which made this CI test appear hung.
    try:
        with page.expect_console_message(
            predicate=lambda message: "[HOOT] Test suite succeeded" in message.text,
            timeout=60_000,
        ) as success_info:
            page.goto(
                f"{BASE_URL}/web/tests?headless&loglevel=2&preset=desktop&timeout=15000&tag=monodoo",
                wait_until="domcontentloaded",
            )
    except PlaywrightTimeoutError as error:
        tail = "\n".join(messages[-30:])
        raise AssertionError(
            "HOOT did not emit its Odoo 19 success signal within 60s. "
            f"url={page.url!r}; console tail:\n{tail}"
        ) from error

    assert "[HOOT] Test suite succeeded" in success_info.value.text
