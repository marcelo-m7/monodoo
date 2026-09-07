# Monodoo Backend Polish — Design

**Status:** Approved as Phase 3A of the Monodoo backend architecture.

## Goal

Add the next reusable backend UX layer without turning `monodoo_theme` into a monolith and without replacing Odoo 19 Community webclient components.

This slice introduces focused presentation addons for standard backend views, chatter, and dialogs, plus a meta-addon that installs the complete stable Monodoo suite.

## Addons

### `monodoo_views`

Depends on `web`, `monodoo_core`, and `monodoo_theme`.

Owns structural visual polish for standard form, list, kanban, search/control-panel, field and button surfaces. It consumes semantic `--monodoo-*` CSS custom properties from `monodoo_theme`; it does not own brand values.

The addon must not patch view controllers, renderers, models, actions, routing, or access logic. Standard Odoo behavior remains authoritative.

### `monodoo_chatter`

Depends on `mail`, `monodoo_core`, and `monodoo_theme`.

Owns responsive presentation for the standard `mail.Chatter` surface. It may style the existing `.o-mail-Chatter` DOM and related standard composer/thread surfaces, but must not replace or fork Chatter Owl components.

### `monodoo_dialog`

Depends on `web`, `monodoo_core`, and `monodoo_theme`.

Owns presentation for standard Odoo dialogs/modals. It styles existing `.o_dialog` / Bootstrap modal surfaces and keeps all standard dialog services, keyboard behavior, focus management, actions, and close semantics.

### `monodoo_backend`

Meta-addon depending on the complete stable generic suite:

- `monodoo_core`
- `monodoo_theme`
- `monodoo_home`
- `monodoo_appsbar`
- `monodoo_views`
- `monodoo_chatter`
- `monodoo_dialog`

It contains no product-specific data and no webclient implementation of its own.

## Visual contract

All new presentation rules must resolve through the existing semantic tokens where applicable:

- `--monodoo-brand`
- `--monodoo-primary`
- `--monodoo-accent`
- `--monodoo-background`
- `--monodoo-surface`
- `--monodoo-text`
- `--monodoo-muted`
- `--monodoo-border`
- `--monodoo-success`
- `--monodoo-warning`
- `--monodoo-danger`
- `--monodoo-radius-sm`
- `--monodoo-radius-md`
- `--monodoo-radius-lg`

No FACODI colors, names, logos, routes, or assumptions may enter these addons.

## UX behavior

The changes are intentionally conservative:

- standard forms receive consistent surface, border and radius treatment;
- list headers/rows and kanban cards gain token-based visual consistency without changing density or data behavior;
- interactive controls receive a visible keyboard focus treatment;
- Chatter gains a token-aligned surface/border treatment and collapses cleanly on narrower screens;
- dialogs gain token-aligned surfaces, borders and responsive margins while preserving Odoo modal behavior;
- reduced-motion preferences are respected for any transitions introduced by these addons.

## Boundaries

Out of scope for this slice:

- authentication or `/odoo` routing changes;
- replacement of Form/List/Kanban/Chatter/Dialog Owl components;
- custom controllers;
- branding assets, login-page branding, or favicon replacement;
- user density preferences;
- command palette / quick actions;
- website-theme synchronization;
- FACODI-specific behavior.

Branding and density remain later Phase 3 slices so they can be implemented with explicit runtime contracts rather than hidden coupling.

## Failure behavior

These addons are CSS/presentation layers. If they are absent, Odoo must remain fully usable with its standard UI. If theme tokens are unavailable, CSS fallbacks from `monodoo_theme` and normal browser/Odoo behavior remain usable.

## Verification

Acceptance requires:

1. repository contracts recognize all new addons and enforce their dependency boundaries;
2. clean Odoo 19 installation succeeds with the full suite;
3. immediate upgrade of the full suite succeeds;
4. existing Home, theme and AppsBar tests remain green;
5. the generic no-FACODI boundary remains green;
6. backend runtime and authenticated browser acceptance remain green;
7. `monodoo_backend` installs the complete stable suite through dependencies only.
