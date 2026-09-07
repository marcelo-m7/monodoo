# Monodoo

Monodoo is a reusable configuration and backend UX layer for **Odoo 19 Community**.

The repository currently provides three generic addons:

- `monodoo_core`: minimal technical base for independent Monodoo capabilities.
- `monodoo_home`: Odoo-native Community Home/application launcher.
- `monodoo_theme`: inheritable backend identity engine with company selection, per-user light/dark/system mode, and semantic runtime CSS tokens.

## Compatibility

- Odoo 19 Community
- LGPL-3

## Installation

Add this repository to the Odoo addons path and update the apps list.

Install `monodoo_home` for the neutral application launcher. Install `monodoo_theme` when you also want backend theme profiles. Both install `monodoo_core` automatically through their declared dependencies.

After an internal user signs in, a neutral backend entry at `http://localhost:8069/odoo` opens the Monodoo Home. Valid Odoo deep links remain handled by the standard webclient.

## Theme hierarchy

`monodoo_theme` treats visual identity as data rather than a hard-coded backend skin. Theme profiles form a parent/child hierarchy: a child only needs to store the semantic tokens it overrides, while unresolved values are inherited from its ancestors.

The resolution order in the first release is:

```text
Monodoo default profile
        ↓
parent theme profile(s)
        ↓
company-selected theme profile
        ↓
user mode preference: system / light / dark
        ↓
effective runtime CSS custom properties
```

A company chooses its backend theme under **Settings → General Settings → Monodoo**. Internal users can choose whether that identity is rendered in system, light, or dark mode from their user preferences. User preferences do not replace the company's institutional identity.

The runtime exposes semantic variables such as:

```text
--monodoo-brand
--monodoo-primary
--monodoo-accent
--monodoo-background
--monodoo-surface
--monodoo-text
--monodoo-muted
--monodoo-border
--monodoo-success
--monodoo-warning
--monodoo-danger
--monodoo-font-family
--monodoo-radius-sm
--monodoo-radius-md
--monodoo-radius-lg
```

Product-specific repositories should define child profiles instead of adding product branding to Monodoo itself. A website-theme companion module can therefore depend on `monodoo_theme`, create a child `monodoo.theme.profile`, and map the website identity into backend tokens without coupling Monodoo to that product. The dedicated Website-to-Backend provider bridge remains a later capability.

## Verification

Fast repository contracts and pure theme-engine tests:

```bash
python3 -m unittest tests.test_repository_contract -v
python3 -m unittest tests.test_theme_tokens -v
node --experimental-default-type=module --test tests/test_theme_runtime.mjs
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

The runtime suite performs a fresh install and upgrade, executes the installed HOOT unit tests, and verifies authenticated desktop/mobile navigation, permissions, local search, deep-link preservation, and the installed Monodoo theme assets.

## Repository boundary

Monodoo is generic and contains no FACODI-specific behavior. Product/deployment repositories may consume released Monodoo addons, but deployment integration and product-specific theme companions belong outside this repository.

See `docs/superpowers/specs/2026-09-05-monodoo-home-design.md` for the Home design and `docs/superpowers/plans/2026-09-07-monodoo-theme-hierarchy-implementation.md` for the Phase 1 theme-engine implementation plan.
