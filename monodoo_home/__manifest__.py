{
    "name": "Monodoo Home",
    "summary": "Native Community application launcher for Odoo 19",
    "version": "19.0.1.0.0",
    "category": "Productivity",
    "author": "Marcelo Santos",
    "website": "https://github.com/marcelo-m7/monodoo",
    "license": "LGPL-3",
    "depends": ["web", "monodoo_core"],
    "data": ["data/home_action.xml"],
    "assets": {
        "web.assets_backend": [
            "monodoo_home/static/src/home/**/*",
            "monodoo_home/static/src/webclient/default_home.js",
        ],
        "web.assets_unit_tests": ["monodoo_home/static/tests/**/*.test.js"],
    },
    "installable": True,
    "application": False,
}
