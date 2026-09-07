from __future__ import annotations

from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    @property
    def SELF_READABLE_FIELDS(self) -> list[str]:
        return super().SELF_READABLE_FIELDS + ["monodoo_theme_mode"]

    @property
    def SELF_WRITEABLE_FIELDS(self) -> list[str]:
        return super().SELF_WRITEABLE_FIELDS + ["monodoo_theme_mode"]

    monodoo_theme_mode = fields.Selection(
        selection=[
            ("system", "System"),
            ("light", "Light"),
            ("dark", "Dark"),
        ],
        string="Monodoo Theme Mode",
        default="system",
        required=True,
    )

    @api.model
    def get_monodoo_theme_context(self) -> dict:
        """Return both variants so the browser can resolve system preference."""
        user = self.env.user
        profile = user.company_id.monodoo_theme_profile_id
        if not profile:
            profile = self.env.ref("monodoo_theme.theme_default", raise_if_not_found=False)
        if not profile:
            return {
                "key": "default",
                "name": "Monodoo Default",
                "mode": user.monodoo_theme_mode,
                "light": {},
                "dark": {},
            }
        return {
            "key": profile.key,
            "name": profile.name,
            "mode": user.monodoo_theme_mode,
            "light": profile._resolved_tokens("light"),
            "dark": profile._resolved_tokens("dark"),
        }
