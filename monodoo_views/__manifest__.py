{
    "name": "Monodoo Views",
    "summary": "Token-driven polish for standard Odoo backend views",
    "version": "19.0.1.0.0",
    "category": "Productivity",
    "author": "Marcelo Santos",
    "website": "https://github.com/marcelo-m7/monodoo",
    "license": "LGPL-3",
    "depends": ["web", "monodoo_core", "monodoo_theme"],
    "data": [],
    "assets": {
        "web.assets_backend": [
            "monodoo_views/static/src/views/**/*.scss",
        ],
    },
    "installable": True,
    "application": False,
}
