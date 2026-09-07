from __future__ import annotations

import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

POLISH_ADDONS = (
    "monodoo_views",
    "monodoo_chatter",
    "monodoo_dialog",
    "monodoo_backend",
)


def load_manifest(addon: str) -> dict:
    return ast.literal_eval((ROOT / addon / "__manifest__.py").read_text(encoding="utf-8"))


class BackendPolishContractTest(unittest.TestCase):
    def test_expected_addons_exist(self):
        for addon in POLISH_ADDONS:
            self.assertTrue((ROOT / addon / "__init__.py").is_file(), addon)
            self.assertTrue((ROOT / addon / "__manifest__.py").is_file(), addon)

    def test_manifests_preserve_modular_dependency_boundaries(self):
        self.assertEqual(
            load_manifest("monodoo_views")["depends"],
            ["web", "monodoo_core", "monodoo_theme"],
        )
        self.assertEqual(
            load_manifest("monodoo_chatter")["depends"],
            ["mail", "monodoo_core", "monodoo_theme"],
        )
        self.assertEqual(
            load_manifest("monodoo_dialog")["depends"],
            ["web", "monodoo_core", "monodoo_theme"],
        )
        self.assertEqual(
            load_manifest("monodoo_backend")["depends"],
            [
                "monodoo_core",
                "monodoo_theme",
                "monodoo_home",
                "monodoo_appsbar",
                "monodoo_views",
                "monodoo_chatter",
                "monodoo_dialog",
            ],
        )

    def test_polish_assets_are_css_only(self):
        expected = {
            "monodoo_views": ["monodoo_views/static/src/views/**/*.scss"],
            "monodoo_chatter": ["monodoo_chatter/static/src/chatter/**/*.scss"],
            "monodoo_dialog": ["monodoo_dialog/static/src/dialog/**/*.scss"],
        }
        for addon, backend_assets in expected.items():
            manifest = load_manifest(addon)
            self.assertEqual(manifest.get("assets", {}).get("web.assets_backend"), backend_assets)
            self.assertEqual(manifest.get("data", []), [])

        backend = load_manifest("monodoo_backend")
        self.assertEqual(backend.get("data", []), [])
        self.assertNotIn("assets", backend)

    def test_polish_addons_are_installable_non_app_lgpl_modules(self):
        for addon in POLISH_ADDONS:
            manifest = load_manifest(addon)
            self.assertEqual(manifest["version"], "19.0.1.0.0")
            self.assertEqual(manifest["license"], "LGPL-3")
            self.assertTrue(manifest["installable"])
            self.assertFalse(manifest["application"])

    def test_no_product_coupling_or_webclient_replacement(self):
        forbidden = (
            "facodi",
            "patch(webclient",
            "patch(formcontroller",
            "patch(listrenderer",
            "patch(kanbanrenderer",
            "t-inherit=\"mail.chatter\"",
            "t-inherit=\"web.dialog\"",
        )
        for addon in POLISH_ADDONS:
            self.assertFalse((ROOT / addon / "controllers").exists())
            for path in (ROOT / addon).rglob("*"):
                if path.is_file() and path.suffix in {".py", ".js", ".xml", ".scss"}:
                    source = path.read_text(encoding="utf-8").lower()
                    for token in forbidden:
                        self.assertNotIn(token, source, str(path))

    def test_styles_consume_semantic_theme_tokens(self):
        view_scss = (ROOT / "monodoo_views/static/src/views/views.scss").read_text(encoding="utf-8")
        chatter_scss = (ROOT / "monodoo_chatter/static/src/chatter/chatter.scss").read_text(encoding="utf-8")
        dialog_scss = (ROOT / "monodoo_dialog/static/src/dialog/dialog.scss").read_text(encoding="utf-8")
        for source in (view_scss, chatter_scss, dialog_scss):
            self.assertIn("var(--monodoo-surface)", source)
            self.assertIn("var(--monodoo-border)", source)
        self.assertIn(":focus-visible", view_scss)
        self.assertIn(".o-mail-Chatter", chatter_scss)
        self.assertIn(".o_dialog", dialog_scss)

    def test_runtime_installs_and_upgrades_complete_suite(self):
        source = (ROOT / "tests/runtime/prepare_database.sh").read_text(encoding="utf-8")
        install = (
            "-i monodoo_core,monodoo_home,monodoo_theme,monodoo_appsbar,"
            "monodoo_views,monodoo_chatter,monodoo_dialog,monodoo_backend,crm,project"
        )
        upgrade = (
            "-u monodoo_core,monodoo_home,monodoo_theme,monodoo_appsbar,"
            "monodoo_views,monodoo_chatter,monodoo_dialog,monodoo_backend"
        )
        self.assertIn(install, source)
        self.assertIn(upgrade, source)


if __name__ == "__main__":
    unittest.main()
