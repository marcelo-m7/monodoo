import { expect, test } from "@odoo/hoot";

import {
    applyThemeContext,
    resolveThemeMode,
} from "@monodoo_theme/theme/theme_runtime";
import { loadThemeContext } from "@monodoo_theme/theme/theme_service";

test.tags("monodoo");
test("theme mode honors explicit light and dark choices", () => {
    expect(resolveThemeMode("light", true)).toBe("light");
    expect(resolveThemeMode("dark", false)).toBe("dark");
});

test.tags("monodoo");
test("system theme mode follows the browser preference", () => {
    expect(resolveThemeMode("system", true)).toBe("dark");
    expect(resolveThemeMode("system", false)).toBe("light");
});

test.tags("monodoo");
test("theme context writes semantic CSS custom properties", () => {
    const root = document.createElement("div");
    const mode = applyThemeContext(
        {
            key: "academy",
            mode: "dark",
            light: { brand: "#111111" },
            dark: { brand: "#eeeeee", font_family: "Inter" },
        },
        root,
        false
    );
    expect(mode).toBe("dark");
    expect(root.dataset.monodooTheme).toBe("dark");
    expect(root.dataset.monodooThemeKey).toBe("academy");
    expect(root.style.getPropertyValue("--monodoo-brand")).toBe("#eeeeee");
    expect(root.style.getPropertyValue("--monodoo-font-family")).toBe("Inter");
});

test.tags("monodoo");
test("loads theme context through the standard ORM service", async () => {
    const orm = {
        call(model, method, args) {
            expect.step(`${model}.${method}:${JSON.stringify(args)}`);
            return Promise.resolve({ key: "default", mode: "system", light: {}, dark: {} });
        },
    };
    const result = await loadThemeContext(orm);
    expect(result.key).toBe("default");
    expect.verifySteps(["res.users.get_monodoo_theme_context:[]"]);
});
