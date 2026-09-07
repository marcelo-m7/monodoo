from __future__ import annotations

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    monodoo_sidebar_mode = fields.Selection(
        selection=[
            ("auto", "Auto"),
            ("expanded", "Expanded"),
            ("compact", "Compact"),
            ("hidden", "Hidden"),
        ],
        string="Monodoo Sidebar",
        default="auto",
        required=True,
    )

    @property
    def SELF_READABLE_FIELDS(self) -> list[str]:
        return super().SELF_READABLE_FIELDS + ["monodoo_sidebar_mode"]

    @property
    def SELF_WRITEABLE_FIELDS(self) -> list[str]:
        return super().SELF_WRITEABLE_FIELDS + ["monodoo_sidebar_mode"]
