from __future__ import annotations

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    monodoo_theme_profile_id = fields.Many2one(
        "monodoo.theme.profile",
        string="Monodoo Backend Theme",
        domain=[("active", "=", True)],
        ondelete="set null",
    )
