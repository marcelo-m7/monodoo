{
    "name": "Monodoo AppsBar",
    "summary": "Odoo-native application sidebar for Community",
    "version": "19.0.1.0.0",
    "category": "Productivity",
    "author": "Marcelo Santos",
    "website": "https://github.com/marcelo-m7/monodoo",
    "license": "LGPL-3",
    "depends": ["web", "monodoo_core"],
    "data": [
        "views/res_users.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "monodoo_appsbar/static/src/appsbar/**/*",
            "monodoo_appsbar/static/src/webclient/**/*",
        ],
        "web.assets_unit_tests": [
            "monodoo_appsbar/static/tests/**/*.test.js",
        ],
    },
    "installable": True,
    "application": False,
}
