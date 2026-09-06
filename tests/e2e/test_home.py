from __future__ import annotations

from playwright.sync_api import Page, expect

from tests.e2e.helpers import BASE_URL, login, wait_for_webclient


def open_neutral_home(page: Page, login_name: str = "admin", password: str = "admin") -> None:
    login(page, login_name, password)
    page.goto(f"{BASE_URL}/odoo", wait_until="domcontentloaded")
    page.locator(".o_monodoo_home").wait_for(state="visible")


def app_card(page: Page, name: str):
    return page.locator(".o_monodoo_app_card").filter(has_text=name)


def test_admin_neutral_odoo_opens_home_with_business_apps(page: Page) -> None:
    open_neutral_home(page)
    expect(page.locator(".o_monodoo_home")).to_be_visible()
    assert page.locator(".o_monodoo_app_card").count() > 1
    expect(app_card(page, "CRM")).to_have_count(1)
    expect(app_card(page, "Project")).to_have_count(1)


def test_valid_crm_deep_link_survives_reload(page: Page) -> None:
    open_neutral_home(page)
    neutral_url = page.url
    app_card(page, "CRM").click()
    page.wait_for_function("neutral => window.location.href !== neutral", arg=neutral_url)
    deep_link = page.url
    page.goto(deep_link, wait_until="domcontentloaded")
    wait_for_webclient(page)
    expect(page.locator(".o_monodoo_home")).to_have_count(0)


def test_project_search_filters_visible_apps(page: Page) -> None:
    open_neutral_home(page)
    page.locator(".o_monodoo_search").fill("Project")
    expect(page.locator(".o_monodoo_app_card")).to_have_count(1)
    expect(app_card(page, "Project")).to_have_count(1)


def test_standard_desktop_apps_dropdown_returns_home(page: Page) -> None:
    open_neutral_home(page)
    app_card(page, "CRM").click()
    page.wait_for_timeout(250)
    page.locator(".o_navbar_apps_menu button").click()
    home_entry = page.locator(".dropdown-menu .o_app").filter(has_text="Home")
    expect(home_entry).to_have_count(1)
    home_entry.click()
    expect(page.locator(".o_monodoo_home")).to_be_visible()


def test_restricted_project_user_does_not_see_crm(page: Page) -> None:
    open_neutral_home(page, "project.user@example.test", "project")
    expect(app_card(page, "Project")).to_have_count(1)
    expect(app_card(page, "CRM")).to_have_count(0)


def test_standard_mobile_apps_sidebar_returns_home(page: Page) -> None:
    page.set_viewport_size({"width": 390, "height": 844})
    open_neutral_home(page)
    app_card(page, "Project").click()
    page.wait_for_timeout(250)
    page.locator("a.o_menu_toggle").click()
    page.locator(".o_sidebar_topbar a.btn-primary").click()
    home_entry = page.locator(".o_app_menu_sidebar li.o_app").filter(has_text="Home")
    expect(home_entry).to_have_count(1)
    home_entry.click()
    expect(page.locator(".o_monodoo_home")).to_be_visible()
