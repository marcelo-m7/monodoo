{
    "name": "Monodoo Theme",
    "summary": "Inheritable backend theme engine for Odoo Community",
    "version": "19.0.1.0.0",
    "category": "Themes/Backend",
    "author": "Marcelo Santos",
    "website": "https://github.com/marcelo-m7/monodoo",
    "license": "LGPL-3",
    "depends": ["base_setup", "web", "monodoo_core"],
    "data": [
        "security/ir.model.access.csv",
        "data/default_theme.xml",
        "data/brand_theme_presets.xml",
        "views/theme_profile_views.xml",
        "views/res_config_settings.xml",
        "views/res_users.xml",
    ],
    "assets": {
        "web.assets_backend": ["monodoo_theme/static/src/theme/**/*"],
        "web.assets_unit_tests": ["monodoo_theme/static/tests/**/*.test.js"],
    },
    "installable": True,
    "application": False,
}
