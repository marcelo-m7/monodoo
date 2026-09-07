# Monodoo Backend Polish — Implementation Plan

## Objective

Implement Phase 3A as small Odoo 19 Community addons that consume `monodoo_theme` tokens while leaving standard webclient behavior intact.

## Task 1 — Extend repository contracts first

Files:
- modify `tests/test_repository_contract.py`
- add `tests/test_backend_polish_contract.py`
- modify `tests/runtime/prepare_database.sh`

Steps:
1. Add `monodoo_views`, `monodoo_chatter`, `monodoo_dialog`, and `monodoo_backend` to the expected addon set.
2. Add failing contract assertions for manifests, exact dependencies, backend asset paths, absence of controllers, no FACODI coupling, and the meta-addon dependency set.
3. Add the new addons to clean-install and upgrade runtime lists.
4. Commit the red contract before implementation.

## Task 2 — Implement `monodoo_views`

Files:
- create `monodoo_views/__init__.py`
- create `monodoo_views/__manifest__.py`
- create `monodoo_views/static/src/views/views.scss`

Steps:
1. Create a non-application LGPL-3 addon depending exactly on `web`, `monodoo_core`, and `monodoo_theme`.
2. Add token-driven form, list, kanban, field/control and focus-visible styling.
3. Keep selectors scoped below `.o_web_client` and avoid controller/renderer patches.
4. Add responsive spacing without changing Odoo data density or behavior.

## Task 3 — Implement `monodoo_chatter`

Files:
- create `monodoo_chatter/__init__.py`
- create `monodoo_chatter/__manifest__.py`
- create `monodoo_chatter/static/src/chatter/chatter.scss`

Steps:
1. Depend exactly on `mail`, `monodoo_core`, and `monodoo_theme`.
2. Style the standard Chatter surface using existing semantic tokens.
3. Add narrow-screen rules that remove unnecessary borders/radii without replacing `mail.Chatter`.

## Task 4 — Implement `monodoo_dialog`

Files:
- create `monodoo_dialog/__init__.py`
- create `monodoo_dialog/__manifest__.py`
- create `monodoo_dialog/static/src/dialog/dialog.scss`

Steps:
1. Depend exactly on `web`, `monodoo_core`, and `monodoo_theme`.
2. Style standard modal content/header/footer and controls using semantic tokens.
3. Add small-screen margins/max-height behavior while retaining standard focus/keyboard semantics.

## Task 5 — Implement the `monodoo_backend` meta-addon

Files:
- create `monodoo_backend/__init__.py`
- create `monodoo_backend/__manifest__.py`

Steps:
1. Depend on the seven stable generic Monodoo addons.
2. Include no data, assets, controllers, models, or product-specific code.
3. Keep `application=False` so it behaves as a composition/meta addon rather than a user-facing Odoo application.

## Task 6 — Documentation

Files:
- modify `README.md`

Steps:
1. Document the new modular layers and the meta-addon.
2. Keep FACODI out of the implementation boundary; mention downstream products only as consumers if needed.
3. Document that branding, density, command palette, and website bridge remain later slices.

## Task 7 — Verification

Run/observe the exact branch head through CI:

1. fast repository contracts;
2. backend-polish contract;
3. existing theme/navigation contracts;
4. clean Odoo 19 install including the new addons;
5. immediate upgrade including the new addons;
6. authenticated Playwright Home/AppsBar acceptance;
7. Monodoo HOOT suite.

Do not merge until the exact head is green. If runtime installation exposes a dependency or asset problem, diagnose from the first failing gate and correct that cause rather than weakening the contract.
