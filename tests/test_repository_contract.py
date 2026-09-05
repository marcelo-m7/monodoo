from __future__ import annotations

import ast
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ADDONS = ("monodoo_core", "monodoo_home")


def load_manifest(addon: str) -> dict:
    return ast.literal_eval((ROOT / addon / "__manifest__.py").read_text(encoding="utf-8"))


class RepositoryContractTest(unittest.TestCase):
    def test_expected_addons_exist(self):
        for addon in ADDONS:
            self.assertTrue((ROOT / addon / "__manifest__.py").is_file())
            self.assertTrue((ROOT / addon / "__init__.py").is_file())

    def test_versions_license_installability(self):
        for addon in ADDONS:
            manifest = load_manifest(addon)
            self.assertEqual(manifest["version"], "19.0.1.0.0")
            self.assertEqual(manifest["license"], "LGPL-3")
            self.assertTrue(manifest["installable"])
            self.assertFalse(manifest["application"])

    def test_dependency_boundary(self):
        self.assertEqual(load_manifest("monodoo_core")["depends"], ["base"])
        self.assertEqual(load_manifest("monodoo_home")["depends"], ["web", "monodoo_core"])

    def test_no_facodi_coupling(self):
        for addon in ADDONS:
            for path in (ROOT / addon).rglob("*"):
                if path.is_file() and path.suffix in {".py", ".js", ".xml", ".scss"}:
                    self.assertNotIn("facodi", path.read_text(encoding="utf-8").lower(), str(path))

    def test_no_controller_package(self):
        for addon in ADDONS:
            self.assertFalse((ROOT / addon / "controllers").exists())

    def test_home_action_and_root_menu_contract(self):
        path = ROOT / "monodoo_home" / "data" / "home_action.xml"
        root = ET.parse(path).getroot()
        action = root.find(".//record[@id='action_monodoo_home']")
        self.assertIsNotNone(action)
        self.assertEqual(action.attrib["model"], "ir.actions.client")
        tag = action.find("./field[@name='tag']")
        self.assertIsNotNone(tag)
        self.assertEqual((tag.text or "").strip(), "monodoo_home")
        menu = root.find(".//menuitem[@id='menu_monodoo_home']")
        self.assertIsNotNone(menu)
        self.assertNotIn("parent", menu.attrib)
        self.assertEqual(menu.attrib["action"], "action_monodoo_home")
        self.assertEqual(menu.attrib["groups"], "base.group_user")
        self.assertEqual(menu.attrib["sequence"], "1")

    def test_home_manifest_declares_task2_assets(self):
        manifest = load_manifest("monodoo_home")
        self.assertEqual(manifest["data"], ["data/home_action.xml"])
        assets = manifest["assets"]
        self.assertEqual(
            assets["web.assets_backend"],
            ["monodoo_home/static/src/home/**/*"],
        )
        self.assertEqual(
            assets["web.assets_unit_tests"],
            ["monodoo_home/static/tests/**/*.test.js"],
        )
        for relative in (
            "data/home_action.xml",
            "static/src/home/constants.js",
            "static/src/home/home.js",
            "static/src/home/home.xml",
            "static/src/home/home.scss",
            "static/tests/home.test.js",
        ):
            self.assertTrue((ROOT / "monodoo_home" / relative).is_file(), relative)


if __name__ == "__main__":
    unittest.main()
