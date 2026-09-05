# Monodoo

Monodoo is a reusable configuration layer for **Odoo 19 Community**.

The first release provides two generic addons:

- `monodoo_core`: minimal technical base for independent Monodoo capabilities.
- `monodoo_home`: Odoo-native Community Home/application launcher.

## Compatibility

- Odoo 19 Community
- LGPL-3

## Installation

Add this repository to the Odoo addons path, update the apps list, then install `monodoo_home`. Odoo installs `monodoo_core` automatically through the declared dependency.

## Repository boundary

Monodoo is generic and contains no FACODI-specific behavior. Product/deployment repositories may consume released Monodoo addons, but deployment integration belongs outside this repository.

See `docs/superpowers/specs/2026-09-05-monodoo-home-design.md` for the approved design.
