import { expect, test } from "@odoo/hoot";
import {
    defineActions,
    defineMenus,
    mountWithCleanup,
    useTestClientAction,
} from "@web/../tests/web_test_helpers";
import { WebClient } from "@web/webclient/webclient";

import { MONODOO_HOME_MENU_XMLID } from "@monodoo_home/home/constants";
import { loadMonodooDefaultApp } from "@monodoo_home/webclient/default_home";
import "@monodoo_home/home/home";

test("default helper selects Home when it is available", async () => {
    const home = { id: 10, xmlid: MONODOO_HOME_MENU_XMLID };
    const menuService = {
        getApps: () => [home, { id: 20, xmlid: "crm.crm_menu_root" }],
        selectMenu: async (menu) => expect.step(`select ${menu.id}`),
    };
    await loadMonodooDefaultApp(menuService, () => expect.step("fallback"));
    expect.verifySteps(["select 10"]);
});

test("default helper falls back when Home is missing", async () => {
    const menuService = {
        getApps: () => [{ id: 20, xmlid: "crm.crm_menu_root" }],
        selectMenu: async () => expect.step("select"),
    };
    await loadMonodooDefaultApp(menuService, () => expect.step("fallback"));
    expect.verifySteps(["fallback"]);
});

test("default helper falls back when Home selection fails", async () => {
    const home = { id: 10, xmlid: MONODOO_HOME_MENU_XMLID };
    const menuService = {
        getApps: () => [home],
        selectMenu: async () => {
            expect.step("select");
            throw new Error("boom");
        },
    };
    await loadMonodooDefaultApp(menuService, () => expect.step("fallback"));
    expect.verifySteps(["select", "fallback"]);
});

test("WebClient opens Monodoo Home when no router state exists", async () => {
    const testAction = useTestClientAction();
    defineActions([
        { id: 1000, name: "Home", tag: "monodoo_home", type: "ir.actions.client" },
        { ...testAction, id: 1001, params: { description: "CRM" } },
    ]);
    defineMenus([
        {
            id: 10,
            name: "Home",
            actionID: 1000,
            xmlid: MONODOO_HOME_MENU_XMLID,
        },
        {
            id: 20,
            name: "CRM",
            actionID: 1001,
            xmlid: "crm.crm_menu_root",
        },
    ]);
    await mountWithCleanup(WebClient);
    expect(".o_monodoo_home").toHaveCount(1);
});
