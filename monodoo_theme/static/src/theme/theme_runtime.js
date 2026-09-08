export const THEME_TOKEN_NAMES = [
    "brand",
    "primary",
    "accent",
    "background",
    "surface",
    "text",
    "muted",
    "border",
    "success",
    "warning",
    "danger",
    "font_family",
    "radius_sm",
    "radius_md",
    "radius_lg",
];

export const SEMANTIC_TOKEN_NAMES = [
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
];

function cssVariableName(token) {
    return `--monodoo-${token.replaceAll("_", "-")}`;
}

export function resolveThemeMode(preference, prefersDark) {
    if (preference === "light" || preference === "dark") {
        return preference;
    }
    return prefersDark ? "dark" : "light";
}

export function applyThemeContext(context, root, prefersDark) {
    const mode = resolveThemeMode(context?.mode, prefersDark);
    const tokens = context?.[mode] || {};

    for (const token of THEME_TOKEN_NAMES) {
        root.style.removeProperty(cssVariableName(token));
    }
    for (const [token, value] of Object.entries(tokens)) {
        if (value !== undefined && value !== null && value !== "") {
            root.style.setProperty(cssVariableName(token), value);
        }
    }

    root.dataset.monodooTheme = mode;
    root.dataset.monodooThemeKey = context?.key || "default";
    return mode;
}
