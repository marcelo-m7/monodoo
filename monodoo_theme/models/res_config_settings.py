from __future__ import annotations

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    monodoo_theme_profile_id = fields.Many2one(
        related="company_id.monodoo_theme_profile_id",
        readonly=False,
        string="Monodoo Backend Theme",
    )
