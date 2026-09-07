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

import { MonodooAppsBar } from "@monodoo_appsbar/appsbar/appsbar";

beforeEach(() => {
    mockService("orm", {
        async read(model) {
            if (model === "res.users") {
                return [{ monodoo_sidebar_mode: "expanded" }];
            }
            return [];
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
            },
        ],
        { mode: "replace" }
    );
});

test.tags("monodoo");
test("renders root applications in Odoo order", async () => {
    await mountWithCleanup(MonodooAppsBar);
    expect(".o_monodoo_appsbar_item").toHaveCount(3);
    expect(".o_monodoo_appsbar_item:nth-child(1) .o_monodoo_appsbar_name").toHaveText("Home");
    expect(".o_monodoo_appsbar_item:nth-child(2) .o_monodoo_appsbar_name").toHaveText("CRM");
    expect(".o_monodoo_appsbar_item:nth-child(3) .o_monodoo_appsbar_name").toHaveText("Project");
});

test.tags("monodoo");
test("applies the per-user sidebar mode", async () => {
    await mountWithCleanup(MonodooAppsBar);
    expect(".o_monodoo_appsbar").toHaveClass("o_monodoo_appsbar_mode_expanded");
});

test.tags("monodoo");
test("highlights the current application", async () => {
    const component = await mountWithCleanup(MonodooAppsBar);
    const crm = component.menuService.getApps()[1];
    patchWithCleanup(component.menuService, {
        getCurrentApp: () => crm,
    });
    component.render();
    await animationFrame();
    expect(".o_monodoo_appsbar_item:nth-child(2)").toHaveClass("active");
});

test.tags("monodoo");
test("opens applications through the standard menu service", async () => {
    const component = await mountWithCleanup(MonodooAppsBar);
    patchWithCleanup(component.menuService, {
        selectMenu(app) {
            expect.step(`select ${app.name}`);
        },
    });
    await contains(".o_monodoo_appsbar_item:nth-child(2) .o_monodoo_appsbar_link").click();
    expect.verifySteps(["select CRM"]);
});
