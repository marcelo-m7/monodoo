import { beforeEach, expect, test } from "@odoo/hoot";
import { animationFrame } from "@odoo/hoot-mock";
import {
    contains,
    defineActions,
    defineMenus,
    mockService,
    mountWithCleanup,
    patchWithCleanup,
    useTestClientAction,
} from "@web/../tests/web_test_helpers";
import { browser } from "@web/core/browser/browser";

import { MonodooHome } from "@monodoo_home/home/home";

let favoriteXmlids;

beforeEach(() => {
    favoriteXmlids = [];
    browser.localStorage.clear();
    mockService("orm", {
        async call(model, method, args) {
            if (model === "res.users" && method === "get_monodoo_navigation_preferences") {
                return { favorite_app_xmlids: favoriteXmlids };
            }
            if (model === "res.users" && method === "set_monodoo_favorite_apps") {
                const values = args[0];
                expect.step(`save ${values.join(",")}`);
                favoriteXmlids = values;
                return values;
            }
            return {};
        },
    });

    const testAction = useTestClientAction();
    defineActions([
        { ...testAction, id: 1000, params: { description: "Home" } },
        { ...testAction, id: 1001, params: { description: "CRM" } },
        { ...testAction, id: 1002, params: { description: "Project" } },
    ]);
    defineMenus(
        [
            {
                id: 10,
                name: "Home",
                actionID: 1000,
                xmlid: "monodoo_home.menu_monodoo_home",
            },
            {
                id: 20,
                name: "CRM",
                actionID: 1001,
                xmlid: "crm.crm_menu_root",
                webIconData: "data:image/png;base64,AA==",
            },
            {
                id: 30,
                name: "Project",
                actionID: 1002,
                xmlid: "project.menu_main_pm",
                webIconData: undefined,
            },
        ],
        { mode: "replace" }
    );
});

test.tags("monodoo");
test("renders permitted apps in Odoo order and excludes Home", async () => {
    await mountWithCleanup(MonodooHome);
    expect(".o_monodoo_all_apps .o_monodoo_app_card").toHaveCount(2);
    expect(".o_monodoo_all_apps .o_monodoo_app_grid > :nth-child(1) .o_monodoo_app_name").toHaveText("CRM");
    expect(".o_monodoo_all_apps .o_monodoo_app_grid > :nth-child(2) .o_monodoo_app_name").toHaveText("Project");
    expect(".o_monodoo_all_apps .o_app_icon").toHaveCount(1);
    expect(".o_monodoo_all_apps .o_monodoo_app_fallback_icon").toHaveCount(1);
});

test.tags("monodoo");
test("renders favorite applications from user preferences", async () => {
    favoriteXmlids = ["project.menu_main_pm"];
    await mountWithCleanup(MonodooHome);
    expect(".o_monodoo_favorites").toHaveCount(1);
    expect(".o_monodoo_favorites .o_monodoo_app_card").toHaveCount(1);
    expect(".o_monodoo_favorites .o_monodoo_app_name").toHaveText("Project");
});

test.tags("monodoo");
test("favorite toggle persists through the res.users preference method", async () => {
    await mountWithCleanup(MonodooHome);
    await contains(".o_monodoo_all_apps .o_monodoo_favorite_toggle").click();
    await animationFrame();
    expect.verifySteps(["save crm.crm_menu_root"]);
    expect(".o_monodoo_favorites .o_monodoo_app_name").toHaveText("CRM");
});

test.tags("monodoo");
test("renders recent applications in most-recent order and excludes Home", async () => {
    const component = await mountWithCleanup(MonodooHome);
    component.state.recentXmlids = [
        "project.menu_main_pm",
        "monodoo_home.menu_monodoo_home",
        "crm.crm_menu_root",
    ];
    await animationFrame();
    expect(".o_monodoo_recent .o_monodoo_app_card").toHaveCount(2);
    expect(".o_monodoo_recent .o_monodoo_app_grid > :nth-child(1) .o_monodoo_app_name").toHaveText("Project");
    expect(".o_monodoo_recent .o_monodoo_app_grid > :nth-child(2) .o_monodoo_app_name").toHaveText("CRM");
});

test.tags("monodoo");
test("filters locally by application name", async () => {
    await mountWithCleanup(MonodooHome);
    await contains(".o_monodoo_search").edit("pro", { confirm: false });
    await animationFrame();
    expect(".o_monodoo_all_apps .o_monodoo_app_card").toHaveCount(1);
    expect(".o_monodoo_all_apps .o_monodoo_app_name").toHaveText("Project");
});

test.tags("monodoo");
test("opens an app through the menu service", async () => {
    const component = await mountWithCleanup(MonodooHome);
    patchWithCleanup(component.menuService, {
        selectMenu(app) {
            expect.step(`select ${app.name}`);
        },
    });
    await contains(".o_monodoo_all_apps .o_monodoo_app_card").click();
    expect.verifySteps(["select CRM"]);
});

test.tags("monodoo");
test("renders an empty state when Home is the only root app", async () => {
    const component = await mountWithCleanup(MonodooHome);
    patchWithCleanup(component.menuService, {
        getApps: () => [
            {
                id: 10,
                name: "Home",
                actionID: 1000,
                xmlid: "monodoo_home.menu_monodoo_home",
            },
        ],
    });
    component.state.query = " ";
    await animationFrame();
    expect(".o_monodoo_app_card").toHaveCount(0);
    expect(".o_monodoo_empty").toHaveCount(1);
});

test.tags("monodoo");
test("typing in search performs no fetch", async () => {
    await mountWithCleanup(MonodooHome);
    patchWithCleanup(browser, {
        fetch: (...args) => {
            expect.step(`fetch ${args[0]}`);
            return Promise.reject(new Error("Search must not fetch"));
        },
    });
    await contains(".o_monodoo_search").edit("crm", { confirm: false });
    await animationFrame();
    expect.verifySteps([]);
});
