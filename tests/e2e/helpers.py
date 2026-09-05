from playwright.sync_api import Page

BASE_URL = "http://127.0.0.1:8069"


def login(page: Page, login_name: str, password: str) -> None:
    page.goto(f"{BASE_URL}/web/login", wait_until="domcontentloaded")
    page.locator("input[name='login']").fill(login_name)
    page.locator("input[name='password']").fill(password)
    page.locator("button[type='submit']").click()
    page.wait_for_load_state("networkidle")
