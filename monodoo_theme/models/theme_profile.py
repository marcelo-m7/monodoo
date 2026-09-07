from __future__ import annotations

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from ..lib.theme_tokens import (
    COLOR_TOKENS,
    COMMON_TOKENS,
    THEME_MODES,
    merge_token_layers,
    token_field_name,
)


class MonodooThemeProfile(models.Model):
    """Reusable backend identity with root-to-leaf token inheritance."""

    _name = "monodoo.theme.profile"
    _description = "Monodoo Theme Profile"
    _order = "name, id"

    name = fields.Char(required=True, translate=True)
    key = fields.Char(required=True, index=True)
    description = fields.Text(translate=True)
    active = fields.Boolean(default=True)
    parent_id = fields.Many2one(
        "monodoo.theme.profile",
        string="Parent Theme",
        ondelete="restrict",
        index=True,
    )
    child_ids = fields.One2many(
        "monodoo.theme.profile",
        "parent_id",
        string="Child Themes",
    )

    light_brand = fields.Char(string="Brand")
    light_primary = fields.Char(string="Primary")
    light_accent = fields.Char(string="Accent")
    light_background = fields.Char(string="Background")
    light_surface = fields.Char(string="Surface")
    light_text = fields.Char(string="Text")
    light_muted = fields.Char(string="Muted Text")
    light_border = fields.Char(string="Border")
    light_success = fields.Char(string="Success")
    light_warning = fields.Char(string="Warning")
    light_danger = fields.Char(string="Danger")

    dark_brand = fields.Char(string="Brand")
    dark_primary = fields.Char(string="Primary")
    dark_accent = fields.Char(string="Accent")
    dark_background = fields.Char(string="Background")
    dark_surface = fields.Char(string="Surface")
    dark_text = fields.Char(string="Text")
    dark_muted = fields.Char(string="Muted Text")
    dark_border = fields.Char(string="Border")
    dark_success = fields.Char(string="Success")
    dark_warning = fields.Char(string="Warning")
    dark_danger = fields.Char(string="Danger")

    font_family = fields.Char(string="Font Family")
    radius_sm = fields.Char(string="Small Radius")
    radius_md = fields.Char(string="Medium Radius")
    radius_lg = fields.Char(string="Large Radius")

    _sql_constraints = [
        (
            "monodoo_theme_profile_key_unique",
            "unique(key)",
            "Theme profile keys must be unique.",
        ),
    ]

    @api.constrains("parent_id")
    def _check_parent_id(self):
        if self._has_cycle():
            raise ValidationError(_("Theme profiles cannot contain recursive parents."))

    def _theme_chain(self):
        """Return Python records ordered from the root profile to ``self``."""
        self.ensure_one()
        chain = []
        current = self
        while current:
            chain.append(current)
            current = current.parent_id
        chain.reverse()
        return chain

    def _token_layer(self, mode: str) -> dict[str, str | None]:
        """Return this profile's explicit token values for one mode."""
        self.ensure_one()
        if mode not in THEME_MODES:
            raise ValidationError(_("Unsupported Monodoo theme mode: %s", mode))
        layer = {
            token: self[token_field_name(token, mode)]
            for token in COLOR_TOKENS
        }
        layer.update({token: self[token] for token in COMMON_TOKENS})
        return layer

    def _resolved_tokens(self, mode: str) -> dict[str, str]:
        """Resolve semantic tokens by applying child overrides over parents."""
        self.ensure_one()
        return merge_token_layers(profile._token_layer(mode) for profile in self._theme_chain())
