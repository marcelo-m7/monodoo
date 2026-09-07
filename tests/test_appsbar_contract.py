from __future__ import annotations

import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class AppsBarContractTest(unittest.TestCase):
    def test_appsbar_addon_boundary(self):
        manifest_path = ROOT / "monodoo_appsbar" / "__manifest__.py"
        self.assertTrue(manifest_path.is_file())
        manifest = ast.literal_eval(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], "19.0.1.0.0")
        self.assertEqual(manifest["license"], "LGPL-3")
        self.assertEqual(manifest["depends"], ["web", "monodoo_core"])
        self.assertTrue(manifest["installable"])
        self.assertFalse(manifest["application"])
        self.assertIn("web.assets_backend", manifest["assets"])
        self.assertIn("web.assets_unit_tests", manifest["assets"])

    def test_sidebar_preference_is_self_managed(self):
        source = (ROOT / "monodoo_appsbar" / "models" / "res_users.py").read_text(encoding="utf-8")
        self.assertIn("monodoo_sidebar_mode", source)
        for value in ("auto", "expanded", "compact", "hidden"):
            self.assertIn(f'("{value}"', source)
        self.assertIn("SELF_READABLE_FIELDS", source)
        self.assertIn("SELF_WRITEABLE_FIELDS", source)

    def test_webclient_extension_preserves_navbar(self):
        js = (ROOT / "monodoo_appsbar" / "static" / "src" / "webclient" / "webclient.js").read_text(encoding="utf-8")
        xml = (ROOT / "monodoo_appsbar" / "static" / "src" / "webclient" / "webclient.xml").read_text(encoding="utf-8")
        self.assertIn("patch(WebClient", js)
        self.assertIn('t-inherit="web.WebClient"', xml)
        self.assertIn("<AppsBar/>", xml)
        self.assertNotIn("patch(NavBar", js)
        self.assertNotIn('t-inherit="web.NavBar"', xml)


if __name__ == "__main__":
    unittest.main()
