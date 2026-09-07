from __future__ import annotations

import ast
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ADDONS = (
    "monodoo_core",
    "monodoo_home",
    "monodoo_theme",
    "monodoo_appsbar",
    "monodoo_views",
    "monodoo_chatter",
    "monodoo_dialog",
    "monodoo_backend",
)


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

    def test_theme_addon_contract(self):
        theme = ROOT / "monodoo_theme"
        self.assertTrue((theme / "__manifest__.py").is_file())
        self.assertTrue((theme / "__init__.py").is_file())
        manifest = load_manifest("monodoo_theme")
        self.assertEqual(manifest["version"], "19.0.1.0.0")
        self.assertEqual(manifest["license"], "LGPL-3")
        self.assertEqual(manifest["depends"], ["base_setup", "web", "monodoo_core"])
        self.assertTrue(manifest["installable"])
        self.assertFalse(manifest["application"])

    def test_dependency_boundary(self):
        self.assertEqual(load_manifest("monodoo_core")["depends"], ["base"])
        self.assertEqual(load_manifest("monodoo_home")["depends"], ["web", "monodoo_core"])
        self.assertEqual(
            load_manifest("monodoo_theme")["depends"],
            ["base_setup", "web", "monodoo_core"],
        )
        self.assertEqual(
            load_manifest("monodoo_appsbar")["depends"],
            ["web", "monodoo_core"],
        )
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

    def test_no_facodi_coupling(self):
        for addon in ADDONS:
            for path in (ROOT / addon).rglob("*"):
                if path.is_file() and path.suffix in {".py", ".js", ".xml", ".scss"}:
                    self.assertNotIn("facodi", path.read_text(encoding="utf-8").lower(), str(path))

    def test_no_controller_package(self):
        for addon in ADDONS:
            self.assertFalse((ROOT / addon / "controllers").exists())

    def test_theme_model_and_configuration_files_exist(self):
        theme = ROOT / "monodoo_theme"
        for relative in (
            "models/__init__.py",
            "models/theme_profile.py",
            "models/res_company.py",
            "models/res_users.py",
            "models/res_config_settings.py",
            "security/ir.model.access.csv",
            "data/default_theme.xml",
            "views/theme_profile_views.xml",
            "views/res_config_settings.xml",
            "views/res_users.xml",
        ):
            self.assertTrue((theme / relative).is_file(), relative)

    def test_theme_manifest_loads_model_data_and_views(self):
        manifest = load_manifest("monodoo_theme")
        self.assertEqual(
            manifest["data"],
            [
                "security/ir.model.access.csv",
                "data/default_theme.xml",
                "views/theme_profile_views.xml",
                "views/res_config_settings.xml",
                "views/res_users.xml",
            ],
        )

    def test_theme_configuration_contract_is_standard_odoo(self):
        theme = ROOT / "monodoo_theme"
        required = [
            theme / "models/theme_profile.py",
            theme / "models/res_users.py",
            theme / "views/res_config_settings.xml",
            theme / "views/theme_profile_views.xml",
        ]
        for path in required:
            self.assertTrue(path.is_file(), str(path.relative_to(ROOT)))
        profile_source = required[0].read_text(encoding="utf-8")
        users_source = required[1].read_text(encoding="utf-8")
        settings_view = required[2].read_text(encoding="utf-8")
        profile_view = required[3].read_text(encoding="utf-8")
        self.assertIn('_name = "monodoo.theme.profile"', profile_source)
        self.assertIn("_has_cycle()", profile_source)
        self.assertIn("def _resolved_tokens", profile_source)
        self.assertIn("SELF_READABLE_FIELDS", users_source)
        self.assertIn("SELF_WRITEABLE_FIELDS", users_source)
        self.assertIn("get_monodoo_theme_context", users_source)
        self.assertIn('inherit_id" ref="base_setup.res_config_settings_view_form"', settings_view)
        self.assertIn("action_monodoo_theme_profiles", profile_view)
        self.assertNotIn("<menuitem", profile_view)

    def test_theme_frontend_asset_contract(self):
        manifest = load_manifest("monodoo_theme")
        assets = manifest["assets"]
        self.assertEqual(
            assets.get("web.assets_backend"),
            ["monodoo_theme/static/src/theme/**/*"],
        )
        self.assertEqual(
            assets.get("web.assets_unit_tests"),
            ["monodoo_theme/static/tests/**/*.test.js"],
        )
        theme = ROOT / "monodoo_theme"
        for relative in (
            "static/src/theme/theme_service.js",
            "static/src/theme/theme.scss",
            "static/tests/theme_service.test.js",
        ):
            self.assertTrue((theme / relative).is_file(), relative)

    def test_theme_frontend_uses_services_not_webclient_patches(self):
        path = ROOT / "monodoo_theme" / "static" / "src" / "theme" / "theme_service.js"
        self.assertTrue(path.is_file(), str(path.relative_to(ROOT)))
        source = path.read_text(encoding="utf-8")
        self.assertIn('registry.category("services").add("monodoo_theme"', source)
        self.assertIn('orm.call("res.users", "get_monodoo_theme_context", [])', source)
        self.assertNotIn("patch(WebClient", source)
        self.assertNotIn("patch(NavBar", source)
        self.assertNotIn('t-inherit="web.NavBar"', source)

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

    def test_home_manifest_declares_assets(self):
        manifest = load_manifest("monodoo_home")
        self.assertEqual(manifest["data"], ["data/home_action.xml"])
        assets = manifest["assets"]
        self.assertEqual(
            assets["web.assets_backend"],
            [
                "monodoo_home/static/src/home/**/*",
                "monodoo_home/static/src/webclient/default_home.js",
            ],
        )
        self.assertEqual(
            assets["web.assets_unit_tests"],
            ["monodoo_home/static/tests/**/*.test.js"],
        )
        for relative in (
            "data/home_action.xml",
            "models/res_users.py",
            "static/src/home/constants.js",
            "static/src/home/navigation_state.js",
            "static/src/home/home.js",
            "static/src/home/home.xml",
            "static/src/home/home.scss",
            "static/src/webclient/default_home.js",
            "static/tests/home.test.js",
            "static/tests/default_home.test.js",
        ):
            self.assertTrue((ROOT / "monodoo_home" / relative).is_file(), relative)

    def test_webclient_patch_boundary(self):
        js_files = list((ROOT / "monodoo_home").rglob("*.js"))
        source = "\n".join(path.read_text(encoding="utf-8") for path in js_files)
        self.assertEqual(source.count("patch(WebClient.prototype"), 1)
        self.assertNotIn("patch(NavBar", source)
        self.assertNotIn('t-inherit="web.NavBar"', source)
        adapter = (
            ROOT / "monodoo_home" / "static" / "src" / "webclient" / "default_home.js"
        ).read_text(encoding="utf-8")
        self.assertIn("_loadDefaultApp()", adapter)
        self.assertNotIn("loadRouterState()", adapter)

    def test_runtime_installs_and_upgrades_complete_backend_suite(self):
        path = ROOT / "tests" / "runtime" / "prepare_database.sh"
        self.assertTrue(path.is_file(), str(path.relative_to(ROOT)))
        source = path.read_text(encoding="utf-8")
        self.assertIn(
            "-i monodoo_core,monodoo_home,monodoo_theme,monodoo_appsbar,monodoo_views,monodoo_chatter,monodoo_dialog,monodoo_backend,crm,project",
            source,
        )
        self.assertIn(
            "-u monodoo_core,monodoo_home,monodoo_theme,monodoo_appsbar,monodoo_views,monodoo_chatter,monodoo_dialog,monodoo_backend",
            source,
        )

    def test_ci_declares_required_release_gates(self):
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        self.assertIn("repository-contract:", workflow)
        self.assertIn("python -m unittest tests.test_appsbar_contract -v", workflow)
        self.assertIn("python -m unittest tests.test_backend_polish_contract -v", workflow)
        self.assertIn("node --experimental-default-type=module --test tests/test_theme_runtime.mjs", workflow)
        self.assertIn("node --experimental-default-type=module --test tests/test_navigation_state.mjs", workflow)
        self.assertIn("odoo-runtime:", workflow)
        self.assertIn("tests/runtime/prepare_database.sh", workflow)
        self.assertIn("pytest tests/e2e/test_home.py -vv -s --maxfail=1", workflow)
        self.assertIn("timeout 90s pytest tests/e2e/test_hoot.py -vv -s --maxfail=1", workflow)
        self.assertIn("timeout-minutes: 12", workflow)


if __name__ == "__main__":
    unittest.main()
