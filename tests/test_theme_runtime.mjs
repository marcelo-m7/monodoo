import assert from "node:assert/strict";
import test from "node:test";

import {
    applyThemeContext,
    resolveThemeMode,
    SEMANTIC_TOKEN_NAMES,
} from "../monodoo_theme/static/src/theme/theme_runtime.js";

function makeRoot() {
    const properties = new Map();
    return {
        dataset: {},
        style: {
            setProperty(name, value) {
                properties.set(name, value);
            },
            removeProperty(name) {
                properties.delete(name);
            },
            getPropertyValue(name) {
                return properties.get(name) || "";
            },
        },
    };
}

test("explicit mode wins over system preference", () => {
    assert.equal(resolveThemeMode("light", true), "light");
    assert.equal(resolveThemeMode("dark", false), "dark");
});

test("system mode follows prefers-color-scheme", () => {
    assert.equal(resolveThemeMode("system", true), "dark");
    assert.equal(resolveThemeMode("system", false), "light");
});

test("theme context applies resolved semantic variables and identity", () => {
    const root = makeRoot();
    const mode = applyThemeContext(
        {
            key: "child",
            mode: "system",
            light: { brand: "#111111", font_family: "Inter" },
            dark: { brand: "#eeeeee", font_family: "Inter" },
        },
        root,
        true,
    );

    assert.equal(mode, "dark");
    assert.equal(root.dataset.monodooTheme, "dark");
    assert.equal(root.dataset.monodooThemeKey, "child");
    assert.equal(root.style.getPropertyValue("--monodoo-brand"), "#eeeeee");
    assert.equal(root.style.getPropertyValue("--monodoo-font-family"), "Inter");
});

test("reapplying a theme removes stale variables", () => {
    const root = makeRoot();
    applyThemeContext(
        { key: "first", mode: "light", light: { brand: "#111111", font_family: "Inter" }, dark: {} },
        root,
        false,
    );
    applyThemeContext(
        { key: "second", mode: "light", light: { brand: "#222222" }, dark: {} },
        root,
        false,
    );

    assert.equal(root.style.getPropertyValue("--monodoo-brand"), "#222222");
    assert.equal(root.style.getPropertyValue("--monodoo-font-family"), "");
});

test("semantic token names remain a stable public contract", () => {
    assert.deepEqual(SEMANTIC_TOKEN_NAMES, [
        "bg",
        "surface_alt",
        "sidebar_bg",
        "navbar_bg",
        "navbar_text",
        "input_bg",
        "hover_bg",
        "active_bg",
        "selected_bg",
        "text_muted",
        "text_disabled",
        "border_subtle",
        "link",
        "link_hover",
        "focus_ring",
        "overlay",
        "on_primary",
        "on_danger",
        "success_bg",
        "warning_bg",
        "danger_bg",
        "code_bg",
        "scrollbar_thumb",
        "scrollbar_track",
    ]);
});
