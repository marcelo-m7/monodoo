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

After an internal user signs in, a neutral backend entry at `http://localhost:8069/odoo` opens the Monodoo Home. Valid Odoo deep links remain handled by the standard webclient.

## Verification

Fast repository contract:

```bash
python3 -m unittest tests.test_repository_contract -v
```

Full Odoo 19 Community acceptance:

```bash
python3 -m venv .venv-test
. .venv-test/bin/activate
pip install -r tests/requirements.txt
python -m playwright install chromium
tests/runtime/prepare_database.sh
pytest tests/e2e -q
cd tests/runtime && docker compose down -v --remove-orphans
```

The runtime suite performs a fresh install and upgrade, executes the installed HOOT unit tests, and verifies authenticated desktop/mobile navigation, permissions, local search, and deep-link preservation.

## Repository boundary

Monodoo is generic and contains no FACODI-specific behavior. Product/deployment repositories may consume released Monodoo addons, but deployment integration belongs outside this repository.

See `docs/superpowers/specs/2026-09-05-monodoo-home-design.md` for the approved design.
