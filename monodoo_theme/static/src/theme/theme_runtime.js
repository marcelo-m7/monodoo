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
