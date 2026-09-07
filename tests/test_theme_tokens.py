from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOKEN_MODULE_PATH = ROOT / "monodoo_theme" / "lib" / "theme_tokens.py"
spec = importlib.util.spec_from_file_location("monodoo_theme_theme_tokens", TOKEN_MODULE_PATH)
assert spec and spec.loader
theme_tokens = importlib.util.module_from_spec(spec)
spec.loader.exec_module(theme_tokens)


class ThemeTokenTest(unittest.TestCase):
    def test_merge_token_layers_uses_root_to_leaf_overrides(self):
        result = theme_tokens.merge_token_layers(
            [
                {"brand": "#111111", "surface": "#ffffff"},
                {"brand": "#222222"},
            ]
        )
        self.assertEqual(result, {"brand": "#222222", "surface": "#ffffff"})

    def test_merge_token_layers_ignores_blank_and_none_values(self):
        result = theme_tokens.merge_token_layers(
            [
                {"brand": "#111111", "surface": "#ffffff"},
                {"brand": "", "surface": None, "accent": "#ff00ff"},
            ]
        )
        self.assertEqual(
            result,
            {"brand": "#111111", "surface": "#ffffff", "accent": "#ff00ff"},
        )

    def test_token_field_name_maps_light_dark_and_common_tokens(self):
        self.assertEqual(theme_tokens.token_field_name("brand", "light"), "light_brand")
        self.assertEqual(theme_tokens.token_field_name("brand", "dark"), "dark_brand")
        self.assertEqual(theme_tokens.token_field_name("font_family", "light"), "font_family")
        self.assertEqual(theme_tokens.token_field_name("font_family", "dark"), "font_family")

    def test_semantic_token_sets_are_stable(self):
        self.assertEqual(
            theme_tokens.COLOR_TOKENS,
            (
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
            ),
        )
        self.assertEqual(
            theme_tokens.COMMON_TOKENS,
            ("font_family", "radius_sm", "radius_md", "radius_lg"),
        )
        self.assertEqual(theme_tokens.THEME_MODES, ("light", "dark"))


if __name__ == "__main__":
    unittest.main()
