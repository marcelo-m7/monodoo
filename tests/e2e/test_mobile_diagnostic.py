from __future__ import annotations

from playwright.sync_api import Page, expect

from tests.e2e.helpers import BASE_URL, login
from tests.e2e.test_home import app_card


def open_mobile_home(page: Page) -> None:
    page.set_viewport_size({"width": 390, "height": 844})
    login(page, "admin", "admin")
    page.goto(f"{BASE_URL}/odoo", wait_until="domcontentloaded")


def open_mobile_project(page: Page) -> None:
    open_mobile_home(page)
    page.locator(".o_monodoo_home").wait_for(state="visible")
    app_card(page, "Project").click()


def mobile_nav_state(page: Page) -> dict:
    return page.locator("a.o_menu_toggle").evaluate(
        """
        (element) => {
            const chain = [];
            let current = element;
            while (current && chain.length < 8) {
                const style = getComputedStyle(current);
                const rect = current.getBoundingClientRect();
                chain.push({
                    tag: current.tagName,
                    className: typeof current.className === "string" ? current.className : "",
                    display: style.display,
                    visibility: style.visibility,
                    opacity: style.opacity,
                    width: rect.width,
                    height: rect.height,
                    x: rect.x,
                    y: rect.y,
                });
                current = current.parentElement;
            }
            return {
                viewport: { width: window.innerWidth, height: window.innerHeight },
                chain,
            };
        }
        """
    )


def test_mobile_neutral_home_is_visible(page: Page) -> None:
    open_mobile_home(page)
    expect(page.locator(".o_monodoo_home")).to_be_visible()


def test_mobile_project_card_is_visible(page: Page) -> None:
    open_mobile_home(page)
    expect(app_card(page, "Project")).to_be_visible()


def test_mobile_project_exposes_standard_menu_toggle(page: Page) -> None:
    open_mobile_project(page)
    toggle = page.locator("a.o_menu_toggle")
    state = mobile_nav_state(page)
    assert toggle.is_visible(), f"MOBILE_NAV_STATE={state!r}"


def test_mobile_menu_toggle_exposes_sidebar_topbar(page: Page) -> None:
    open_mobile_project(page)
    page.locator("a.o_menu_toggle").click()
    expect(page.locator(".o_sidebar_topbar a.btn-primary")).to_be_visible()


def test_mobile_sidebar_topbar_exposes_home_app(page: Page) -> None:
    open_mobile_project(page)
    page.locator("a.o_menu_toggle").click()
    page.locator(".o_sidebar_topbar a.btn-primary").click()
    expect(page.locator(".o_app_menu_sidebar li.o_app").filter(has_text="Home")).to_have_count(1)


def test_mobile_home_app_returns_to_monodoo_home(page: Page) -> None:
    open_mobile_project(page)
    page.locator("a.o_menu_toggle").click()
    page.locator(".o_sidebar_topbar a.btn-primary").click()
    page.locator(".o_app_menu_sidebar li.o_app").filter(has_text="Home").click()
    expect(page.locator(".o_monodoo_home")).to_be_visible()
