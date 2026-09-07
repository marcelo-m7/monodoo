{
    "name": "Monodoo Dialog",
    "summary": "Responsive token-driven presentation for Odoo dialogs",
    "version": "19.0.1.0.0",
    "category": "Productivity",
    "author": "Marcelo Santos",
    "website": "https://github.com/marcelo-m7/monodoo",
    "license": "LGPL-3",
    "depends": ["web", "monodoo_core", "monodoo_theme"],
    "data": [],
    "assets": {
        "web.assets_backend": [
            "monodoo_dialog/static/src/dialog/**/*.scss",
        ],
    },
    "installable": True,
    "application": False,
}
