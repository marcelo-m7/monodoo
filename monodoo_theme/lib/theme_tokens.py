from __future__ import annotations

from collections.abc import Iterable, Mapping

COLOR_TOKENS = (
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
)
COMMON_TOKENS = ("font_family", "radius_sm", "radius_md", "radius_lg")
THEME_MODES = ("light", "dark")


def merge_token_layers(layers: Iterable[Mapping[str, str | None]]) -> dict[str, str]:
    """Merge root-to-leaf theme layers, ignoring empty override values."""
    merged: dict[str, str] = {}
    for layer in layers:
        for token, value in layer.items():
            if value not in (None, ""):
                merged[token] = value
    return merged


def token_field_name(token: str, mode: str) -> str:
    """Return the profile field that stores one semantic token."""
    if token in COMMON_TOKENS:
        return token
    if token not in COLOR_TOKENS:
        raise ValueError(f"Unknown theme token: {token}")
    if mode not in THEME_MODES:
        raise ValueError(f"Unknown theme mode: {mode}")
    return f"{mode}_{token}"
