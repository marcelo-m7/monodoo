# Monodoo

Monodoo is a reusable configuration and backend UX layer for **Odoo 19 Community**.

The repository currently provides eight generic addons:

- `monodoo_core`: minimal technical base for independent Monodoo capabilities.
- `monodoo_home`: Odoo-native Community Home/application launcher with favorites, recents, and local search.
- `monodoo_theme`: inheritable backend identity engine with company selection, per-user light/dark/system mode, semantic runtime CSS tokens, and reusable identity presets.
- `monodoo_appsbar`: responsive application sidebar built on Odoo's standard menu service.
- `monodoo_views`: token-driven polish for standard form, list, kanban and backend control surfaces.
- `monodoo_chatter`: responsive presentation layer for the standard Odoo Chatter.
- `monodoo_dialog`: responsive presentation layer for standard Odoo dialogs.
- `monodoo_backend`: meta-addon that installs the complete stable Monodoo backend suite.

## Compatibility

- Odoo 19 Community
- LGPL-3

## Installation

Add this repository to the Odoo addons path and update the apps list.

Install only the capabilities you need, or install `monodoo_backend` to compose the complete stable backend suite.

The presentation addons remain intentionally modular. `monodoo_appsbar` deliberately does **not** depend on `monodoo_theme`; when both are installed the sidebar consumes the shared CSS custom properties naturally, while remaining usable with neutral Odoo-compatible fallbacks on its own. `monodoo_views`, `monodoo_chatter`, and `monodoo_dialog` depend on `monodoo_theme` because their presentation contract is explicitly token-driven.

After an internal user signs in, a neutral backend entry at `http://localhost:8069/odoo` opens the Monodoo Home. Valid Odoo deep links remain handled by the standard webclient.

## Home navigation

The Home continues to source applications from Odoo's existing menu service, so Odoo remains authoritative for ordering and access. Phase 2 adds three presentation layers without introducing another menu or security model:

- **Favorites** are stored as a per-user presentation preference and sanitized against root applications the current user can actually access.
- **Recent applications** are stored locally in the browser, isolated by database and user, deduplicated, and bounded to the six most recent applications.
- **All applications** preserves the original authorized Odoo order and remains searchable entirely client-side.

Selecting an application always delegates to `menuService.selectMenu(app)`. The Monodoo Home root menu is excluded from business-app favorites and recents.

## AppsBar

`monodoo_appsbar` adds application navigation beside the standard Odoo action area while leaving the standard navbar and mobile application flow intact. It reads the same authorized root applications already loaded by Odoo and never performs a `sudo()` menu lookup.

Internal users can choose one of four sidebar modes from their user preferences:

| Mode | Behavior |
| --- | --- |
| `Auto` | Expanded on wide desktops, compact on medium screens, hidden on mobile. |
| `Expanded` | 13rem sidebar with application icon and name. |
| `Compact` | 4rem icon-first sidebar with accessible application titles. |
| `Hidden` | No Monodoo sidebar; standard Odoo navigation remains available. |

The current application is highlighted using Odoo's `getCurrentApp()` state and all application changes are opened through the standard menu service.

## Theme hierarchy

`monodoo_theme` treats visual identity as data rather than a hard-coded backend skin. Theme profiles form a parent/child hierarchy: a child can override semantic tokens while unresolved values are inherited from its ancestors.

The resolution order is:

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

`monodoo_theme` ships with a neutral default plus four selectable ecosystem presets. Each preset provides complete light/dark semantic tokens while still inheriting from the default profile so future shared defaults remain composable:

| Preset | Intent |
| --- | --- |
| `Monodoo Default` | Neutral Odoo-compatible baseline. |
| `Open2 Tech` | Clean technical/corporate identity inspired by the Open2 Tech ecosystem. |
| `O2 Tube` | Media-first, high-contrast identity inspired by O2 Tube. |
| `FACODI` | Community-learning identity using FACODI's ink/cyan/blue/mint/sun visual language. |
| `Monynha Softwares` | Product-studio identity for the wider Monynha ecosystem. |

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

All standard backend surfaces consume the derived semantic roles from the same
layer. Important roles include `--monodoo-bg`, `--monodoo-surface-alt`,
`--monodoo-sidebar-bg`, `--monodoo-navbar-bg`, `--monodoo-input-bg`,
`--monodoo-hover-bg`, `--monodoo-active-bg`, `--monodoo-selected-bg`,
`--monodoo-text-muted`, `--monodoo-text-disabled`, `--monodoo-link`,
`--monodoo-focus-ring`, `--monodoo-overlay`, and the success/warning/danger
surface roles. These aliases resolve from the active identity tokens, so a
new module using standard Odoo components inherits light and dark behavior
without a Monodoo-specific stylesheet.

Additional deployments can define more child profiles without changing the backend engine. A website-theme companion module can depend on `monodoo_theme`, create a child `monodoo.theme.profile`, and map a website identity into backend tokens. The dedicated Website-to-Backend provider bridge remains a later capability.

## Backend polish

Phase 3A keeps the standard Odoo components and adds presentation only:

- `monodoo_views` aligns form sheets, list tables, kanban records, controls and keyboard-focus states with semantic theme tokens;
- `monodoo_chatter` styles the existing `mail.Chatter` surface and keeps it usable on narrower screens;
- `monodoo_dialog` styles the existing Odoo dialog/modal surface and adds conservative small-screen sizing;
- `monodoo_backend` installs the stable suite through dependencies only and contains no runtime implementation of its own.

These addons do not replace Form/List/Kanban controllers or renderers, do not fork Chatter/Dialog Owl components, and do not introduce custom `/odoo` routing or controllers. Branding assets, user density preferences, command palette/quick actions, and Website-to-Backend synchronization remain separate later slices.

## Verification

Fast repository contracts and dependency-free engine tests:

```bash
python3 -m unittest tests.test_repository_contract -v
python3 -m unittest tests.test_theme_tokens -v
python3 -m unittest tests.test_navigation_models -v
python3 -m unittest tests.test_home_navigation_contract -v
python3 -m unittest tests.test_appsbar_contract -v
python3 -m unittest tests.test_backend_polish_contract -v
node --experimental-default-type=module --test tests/test_theme_runtime.mjs
node --experimental-default-type=module --test tests/test_navigation_state.mjs
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

The runtime suite performs a fresh install and upgrade of the complete stable Monodoo backend suite, executes the installed HOOT tests, and verifies authenticated desktop/mobile navigation, permissions, local search, deep-link preservation, theme assets, favorites/recents behavior, and AppsBar menu-service integration.

## Repository boundary

Monodoo keeps product behavior outside the generic backend engine. The bundled theme presets are reusable identity data only: they add no FACODI, Open2, O2 Tube, or Monynha business logic. Deployment integrations, website-specific components, and product workflows remain in their respective repositories.

Design and implementation documents:

- `docs/superpowers/specs/2026-09-05-monodoo-home-design.md`
- `docs/superpowers/plans/2026-09-07-monodoo-theme-hierarchy-implementation.md`
- `docs/superpowers/specs/2026-09-07-monodoo-navigation-design.md`
- `docs/superpowers/plans/2026-09-07-monodoo-navigation-implementation.md`
- `docs/superpowers/specs/2026-09-07-monodoo-backend-polish-design.md`
- `docs/superpowers/plans/2026-09-07-monodoo-backend-polish-implementation.md`
