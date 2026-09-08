from __future__ import annotations

import ast
import importlib.util
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

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
        self.assertEqual(
            theme_tokens.SEMANTIC_TOKENS,
            (
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
            ),
        )
        self.assertEqual(theme_tokens.THEME_MODES, ("light", "dark"))

    def test_brand_theme_presets_are_installed_and_complete(self):
        manifest = ast.literal_eval((ROOT / "monodoo_theme" / "__manifest__.py").read_text())
        self.assertIn("data/brand_theme_presets.xml", manifest["data"])

        preset_path = ROOT / "monodoo_theme" / "data" / "brand_theme_presets.xml"
        self.assertTrue(preset_path.exists())
        root = ET.parse(preset_path).getroot()
        records = root.findall(".//record[@model='monodoo.theme.profile']")
        by_key = {
            record.find("field[@name='key']").text: record
            for record in records
            if record.find("field[@name='key']") is not None
        }

        expected_keys = {"open2-tech", "o2-tube", "facodi", "monynha-softwares"}
        self.assertEqual(expected_keys, set(by_key))

        required_fields = {
            *(f"{mode}_{token}" for mode in ("light", "dark") for token in theme_tokens.COLOR_TOKENS),
            *theme_tokens.COMMON_TOKENS,
        }
        for key, record in by_key.items():
            field_names = {field.attrib.get("name") for field in record.findall("field")}
            self.assertTrue(required_fields <= field_names, f"{key} is missing theme tokens")
            parent = record.find("field[@name='parent_id']")
            self.assertIsNotNone(parent, f"{key} should inherit from Monodoo Default")
            self.assertEqual(parent.attrib.get("ref"), "monodoo_theme.theme_default")


if __name__ == "__main__":
    unittest.main()
