import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";

import { applyThemeContext } from "./theme_runtime";

const DARK_MODE_QUERY = "(prefers-color-scheme: dark)";

export const FALLBACK_THEME_CONTEXT = {
    key: "default",
    name: "Monodoo Default",
    mode: "system",
    light: {},
    dark: {},
};

export function loadThemeContext(orm) {
    return orm.call("res.users", "get_monodoo_theme_context", []);
}

export const monodooThemeService = {
    dependencies: ["orm"],
    async start(env, { orm }) {
        const media = browser.matchMedia(DARK_MODE_QUERY);
        let context = FALLBACK_THEME_CONTEXT;

        const apply = () =>
            applyThemeContext(context, document.documentElement, media.matches);

        const reload = async () => {
            try {
                context = (await loadThemeContext(orm)) || FALLBACK_THEME_CONTEXT;
            } catch (error) {
                browser.console.warn(
                    "Monodoo Theme failed to load; keeping neutral runtime defaults",
                    error
                );
                context = FALLBACK_THEME_CONTEXT;
            }
            apply();
            return context;
        };

        await reload();

        media.addEventListener?.("change", () => {
            if (context.mode === "system") {
                apply();
            }
        });

        return {
            apply,
            reload,
            get context() {
                return context;
            },
        };
    },
};

registry.category("services").add("monodoo_theme", monodooThemeService);
