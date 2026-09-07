from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class NavigationModelContractTest(unittest.TestCase):
    def test_home_user_preferences_are_self_readable_and_writeable(self):
        source = (ROOT / "monodoo_home" / "models" / "res_users.py").read_text(encoding="utf-8")
        self.assertIn("monodoo_favorite_app_xmlids", source)
        self.assertIn("SELF_READABLE_FIELDS", source)
        self.assertIn("SELF_WRITEABLE_FIELDS", source)
        self.assertIn("get_monodoo_navigation_preferences", source)
        self.assertIn("set_monodoo_favorite_apps", source)


if __name__ == "__main__":
    unittest.main()
