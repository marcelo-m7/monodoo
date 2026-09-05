from playwright.sync_api import Page

BASE_URL = "http://127.0.0.1:8069"


def wait_for_webclient(page: Page) -> None:
    """Wait for the Odoo SPA shell instead of network idleness.

    Odoo keeps a websocket open for the bus service, so a logged-in backend
    session is not expected to become network-idle.
    """
    page.wait_for_url("**/odoo**")
    page.locator(".o_main_navbar").wait_for(state="visible")


def login(page: Page, login_name: str, password: str) -> None:
    page.goto(f"{BASE_URL}/web/login", wait_until="domcontentloaded")
    page.locator("input[name='login']").fill(login_name)
    page.locator("input[name='password']").fill(password)
    page.locator("button[type='submit']").click()
    wait_for_webclient(page)
