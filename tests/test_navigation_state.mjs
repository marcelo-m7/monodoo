import test from "node:test";
import assert from "node:assert/strict";

import {
    getRecentStorageKey,
    normalizeRecentApps,
} from "../monodoo_home/static/src/home/navigation_state.js";

test("recent apps are unique, most-recent first, and bounded", () => {
    assert.deepEqual(
        normalizeRecentApps(["crm.crm_menu_root", "project.menu_main_pm", "crm.crm_menu_root"], "sale.sale_menu_root", 3),
        ["sale.sale_menu_root", "crm.crm_menu_root", "project.menu_main_pm"]
    );
});

test("selecting an existing recent app moves it to the front", () => {
    assert.deepEqual(
        normalizeRecentApps(["crm.crm_menu_root", "project.menu_main_pm"], "project.menu_main_pm", 6),
        ["project.menu_main_pm", "crm.crm_menu_root"]
    );
});

test("storage keys isolate database and user", () => {
    assert.equal(
        getRecentStorageKey("monodoo_test", 7),
        "monodoo:recent-apps:monodoo_test:7"
    );
});
