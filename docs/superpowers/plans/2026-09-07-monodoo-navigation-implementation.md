# Monodoo Navigation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a modular AppsBar and enrich Monodoo Home with favorites and recent applications while preserving Odoo 19 Community navigation and security semantics.

**Architecture:** `monodoo_appsbar` is a standalone WebClient extension that consumes the standard menu service and per-user sidebar preference. `monodoo_home` gains a small navigation-preferences service for favorites and bounded local recents, but continues opening apps exclusively through `menuService.selectMenu`.

**Tech Stack:** Odoo 19 Community, Owl, Odoo web registry/services, QWeb XML, SCSS, Python ORM, HOOT, unittest, Playwright runtime CI.

**Spec:** `docs/superpowers/specs/2026-09-07-monodoo-navigation-design.md`

## Global Constraints

- Odoo 19 Community only.
- LGPL-3.
- No FACODI-specific code.
- No custom `/odoo` controller or authentication/router replacement.
- No second ACL/menu model; visible apps come from Odoo's menu service.
- Standard navbar/mobile navigation remains available.
- `monodoo_appsbar` must not require `monodoo_theme`.
- Favorites never grant access; recents are presentation-only.

---

### Task 1: Navigation preference primitives

**Files:**
- Create: `monodoo_home/models/res_users.py`
- Create: `monodoo_home/models/__init__.py`
- Modify: `monodoo_home/__init__.py`
- Create: `monodoo_home/static/src/home/navigation_state.js`
- Test: `tests/test_navigation_state.mjs`
- Test: `tests/test_repository_contract.py`

**Interfaces:**
- Produces `res.users.monodoo_favorite_app_xmlids` as JSON text and `get_monodoo_navigation_preferences()` / `set_monodoo_favorite_apps(xmlids)` ORM methods.
- Produces `normalizeRecentApps(xmlids, selectedXmlid, limit=6)` and storage helper functions used by Home.

- [ ] Write failing Python/repository-contract and Node tests for the field/method contracts and recent ordering/deduplication/bounds.
- [ ] Run the focused tests and confirm they fail because the new interfaces do not exist.
- [ ] Implement the minimal model and dependency-free JS helpers.
- [ ] Run the focused tests and confirm they pass.

### Task 2: Enriched Home

**Files:**
- Modify: `monodoo_home/static/src/home/home.js`
- Modify: `monodoo_home/static/src/home/home.xml`
- Modify: `monodoo_home/static/src/home/home.scss`
- Modify: `monodoo_home/static/tests/home.test.js`

**Interfaces:**
- Consumes navigation preference primitives from Task 1 and Odoo `menu`/`orm` services.
- Produces `favoriteApps`, `recentApps`, `allApps`, `toggleFavorite(app)`, and recent tracking on app selection.

- [ ] Add failing HOOT tests for favorite sections, favorite toggle delegation, recent ordering, Home exclusion, and unchanged local search/menu selection.
- [ ] Run HOOT in CI and verify red failures correspond to missing Home behavior.
- [ ] Implement minimal Home behavior and accessible favorite controls.
- [ ] Run HOOT and preserve all existing Home/default-route tests.

### Task 3: `monodoo_appsbar`

**Files:**
- Create: `monodoo_appsbar/__init__.py`
- Create: `monodoo_appsbar/__manifest__.py`
- Create: `monodoo_appsbar/models/__init__.py`
- Create: `monodoo_appsbar/models/res_users.py`
- Create: `monodoo_appsbar/views/res_users.xml`
- Create: `monodoo_appsbar/static/src/appsbar/appsbar.js`
- Create: `monodoo_appsbar/static/src/appsbar/appsbar.xml`
- Create: `monodoo_appsbar/static/src/appsbar/appsbar.scss`
- Create: `monodoo_appsbar/static/src/webclient/webclient.js`
- Create: `monodoo_appsbar/static/src/webclient/webclient.xml`
- Create: `monodoo_appsbar/static/tests/appsbar.test.js`
- Modify: `tests/test_repository_contract.py`

**Interfaces:**
- Produces `res.users.monodoo_sidebar_mode` with `auto|expanded|compact|hidden` and self-readable/self-writeable semantics.
- Produces `MonodooAppsBar`, rendered after standard `NavBar`, using `menu.getApps()`, `menu.getCurrentApp()`, and `menu.selectMenu(app)`.

- [ ] Add failing contract/HOOT tests for addon boundaries, modes, authorized ordered apps, active state, and menu-service delegation.
- [ ] Run focused tests and confirm red.
- [ ] Implement the addon and the single WebClient component/template extension.
- [ ] Run focused tests and confirm green.

### Task 4: Runtime and release gates

**Files:**
- Modify: `tests/runtime/prepare_database.sh`
- Modify: `.github/workflows/ci.yml`
- Modify: `README.md`

**Interfaces:**
- Runtime install/upgrade set becomes `monodoo_core,monodoo_home,monodoo_theme,monodoo_appsbar`.

- [ ] Update repository contract expectations and runtime install/upgrade commands.
- [ ] Run full repository contract, pure Node tests, Odoo install/upgrade, E2E launcher tests, and HOOT suite.
- [ ] Update README with installation, module boundaries, sidebar modes, favorites/recents, and verification commands.
- [ ] Compare branch against Phase 1 and verify only navigation-phase files changed.
