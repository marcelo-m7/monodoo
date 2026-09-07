from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class HomeNavigationContractTest(unittest.TestCase):
    def test_home_exposes_favorites_and_recents_behavior(self):
        js = (ROOT / "monodoo_home" / "static" / "src" / "home" / "home.js").read_text(encoding="utf-8")
        for symbol in (
            "favoriteApps",
            "recentApps",
            "toggleFavorite",
            "get_monodoo_navigation_preferences",
            "normalizeRecentApps",
            "getRecentStorageKey",
        ):
            self.assertIn(symbol, js)

    def test_home_template_has_navigation_sections(self):
        xml = (ROOT / "monodoo_home" / "static" / "src" / "home" / "home.xml").read_text(encoding="utf-8")
        self.assertIn("o_monodoo_favorites", xml)
        self.assertIn("o_monodoo_recent", xml)
        self.assertIn("o_monodoo_all_apps", xml)
        self.assertIn("o_monodoo_favorite_toggle", xml)


if __name__ == "__main__":
    unittest.main()
