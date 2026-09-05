from __future__ import annotations

import ast
from pathlib import Path
import unittest

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


if __name__ == "__main__":
    unittest.main()
