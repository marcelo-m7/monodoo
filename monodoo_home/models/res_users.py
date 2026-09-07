from __future__ import annotations

import json

from odoo import api, fields, models


HOME_MENU_XMLID = "monodoo_home.menu_monodoo_home"


class ResUsers(models.Model):
    _inherit = "res.users"

    monodoo_favorite_app_xmlids = fields.Text(
        string="Monodoo Favorite Applications",
        default="[]",
    )

    @property
    def SELF_READABLE_FIELDS(self) -> list[str]:
        return super().SELF_READABLE_FIELDS + ["monodoo_favorite_app_xmlids"]

    @property
    def SELF_WRITEABLE_FIELDS(self) -> list[str]:
        return super().SELF_WRITEABLE_FIELDS + ["monodoo_favorite_app_xmlids"]

    @api.model
    def _monodoo_allowed_root_app_xmlids(self) -> set[str]:
        roots = self.env["ir.ui.menu"].load_menus_root().get("children", [])
        return {
            item["xmlid"]
            for item in roots
            if item.get("xmlid") and item["xmlid"] != HOME_MENU_XMLID
        }

    def _monodoo_decode_favorites(self) -> list[str]:
        self.ensure_one()
        try:
            values = json.loads(self.monodoo_favorite_app_xmlids or "[]")
        except (TypeError, ValueError, json.JSONDecodeError):
            return []
        if not isinstance(values, list):
            return []
        return [value for value in values if isinstance(value, str) and value]

    @api.model
    def get_monodoo_navigation_preferences(self) -> dict:
        allowed = self._monodoo_allowed_root_app_xmlids()
        favorites = []
        for xmlid in self.env.user._monodoo_decode_favorites():
            if xmlid in allowed and xmlid not in favorites:
                favorites.append(xmlid)
        return {"favorite_app_xmlids": favorites}

    @api.model
    def set_monodoo_favorite_apps(self, xmlids) -> list[str]:
        if not isinstance(xmlids, list):
            xmlids = []
        allowed = self._monodoo_allowed_root_app_xmlids()
        cleaned = []
        for xmlid in xmlids:
            if isinstance(xmlid, str) and xmlid in allowed and xmlid not in cleaned:
                cleaned.append(xmlid)
        self.env.user.write({"monodoo_favorite_app_xmlids": json.dumps(cleaned)})
        return cleaned
