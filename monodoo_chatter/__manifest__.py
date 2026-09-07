{
    "name": "Monodoo Chatter",
    "summary": "Responsive token-driven presentation for Odoo Chatter",
    "version": "19.0.1.0.0",
    "category": "Productivity",
    "author": "Marcelo Santos",
    "website": "https://github.com/marcelo-m7/monodoo",
    "license": "LGPL-3",
    "depends": ["mail", "monodoo_core", "monodoo_theme"],
    "data": [],
    "assets": {
        "web.assets_backend": [
            "monodoo_chatter/static/src/chatter/**/*.scss",
        ],
    },
    "installable": True,
    "application": False,
}
