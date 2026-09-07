# Monodoo Theme Hierarchy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the first Monodoo backend theme engine for Odoo 19 Community: inheritable theme profiles, company selection, per-user light/dark/system preference, semantic CSS tokens, and a backend service that applies the resolved theme without replacing the Odoo webclient.

**Architecture:** `monodoo_theme` is a standalone addon on top of `monodoo_core`, `web`, and `base_setup`. Theme profiles form a parent/child tree; server-side resolution merges root-to-leaf token layers, company configuration chooses the profile, and the current user's mode preference chooses light/dark/system on the client. The frontend registers an Odoo service and applies CSS custom properties to the document root, preserving standard actions, menus, routing, authentication, and ACL behavior.

**Tech Stack:** Odoo 19 Community, Python/Odoo ORM, XML views/data, Owl/web service registry, SCSS/CSS custom properties, HOOT, Python unittest.

**Spec:** Approved conversation design on 2026-09-07; this plan implements Phase 1 (`monodoo_theme`) only.

## Global Constraints

- Target Odoo 19 Community only.
- License LGPL-3.
- Keep `monodoo_core` minimal and generic.
- No FACODI-specific code or values in Monodoo addons.
- Do not replace the Odoo webclient, navbar, authentication, router, or menu security.
- Use standard Odoo services and models.
- Theme hierarchy is root-to-leaf with child overrides.
- Company chooses the effective theme profile; user controls only `system`, `light`, or `dark` mode in Phase 1.
- Use CSS custom properties for runtime theme identity.
- Preserve current `monodoo_home` behavior and dependency boundary.

---

### Task 1: Repository contract and pure token-resolution engine

**Files:**
- Create: `monodoo_theme/__init__.py`
- Create: `monodoo_theme/__manifest__.py`
- Create: `monodoo_theme/lib/__init__.py`
- Create: `monodoo_theme/lib/theme_tokens.py`
- Create: `tests/test_theme_tokens.py`
- Modify: `tests/test_repository_contract.py`

**Interfaces:**
- Produces: `merge_token_layers(layers: list[dict[str, str | None]]) -> dict[str, str]`
- Produces: `token_field_name(token: str, mode: str) -> str`
- Produces: `COLOR_TOKENS`, `COMMON_TOKENS`, `THEME_MODES`

- [ ] Add failing repository-contract assertions for `monodoo_theme` manifest, dependencies, data/assets, generic boundary, and expected files.
- [ ] Run `python -m unittest tests.test_repository_contract -v` and confirm failure because `monodoo_theme` does not exist.
- [ ] Add failing pure unit tests proving root-to-leaf merge, blank-value omission, common token handling, and light/dark field-name mapping.
- [ ] Run `python -m unittest tests.test_theme_tokens -v` and confirm failure because the token engine is missing.
- [ ] Implement the minimal manifest/package and pure token-resolution helper.
- [ ] Run both unittest modules and require green.
- [ ] Commit `feat: add monodoo theme token engine`.

### Task 2: Odoo hierarchy models and configuration UI

**Files:**
- Create: `monodoo_theme/models/__init__.py`
- Create: `monodoo_theme/models/theme_profile.py`
- Create: `monodoo_theme/models/res_company.py`
- Create: `monodoo_theme/models/res_users.py`
- Create: `monodoo_theme/models/res_config_settings.py`
- Create: `monodoo_theme/security/ir.model.access.csv`
- Create: `monodoo_theme/data/default_theme.xml`
- Create: `monodoo_theme/views/theme_profile_views.xml`
- Create: `monodoo_theme/views/res_config_settings.xml`
- Create: `monodoo_theme/views/res_users.xml`
- Modify: `tests/test_repository_contract.py`

**Interfaces:**
- Produces model: `monodoo.theme.profile`
- Produces method: `monodoo.theme.profile._resolved_tokens(mode: str) -> dict[str, str]`
- Produces field: `res.company.monodoo_theme_profile_id`
- Produces field: `res.users.monodoo_theme_mode`
- Produces RPC: `res.users.get_monodoo_theme_context() -> dict`
- Produces setting: `res.config.settings.monodoo_theme_profile_id`

- [ ] Add failing structural tests for model files, access CSV, default profile XML, settings/action views, user preference field declaration, and no root Monodoo menu.
- [ ] Run repository-contract tests and confirm the new assertions fail.
- [ ] Implement `monodoo.theme.profile` with unique key, parent hierarchy, `_has_cycle()` constraint, root-to-leaf merge, and light/dark/common semantic token fields.
- [ ] Implement company selection, user mode preference with self-readable/self-writeable fields, and `get_monodoo_theme_context()` fallback to `monodoo_theme.theme_default`.
- [ ] Add administrator-only profile CRUD access and internal-user read access.
- [ ] Add the neutral Odoo-compatible default profile and Settings/Profile/User views.
- [ ] Run repository-contract and pure token tests and require green.
- [ ] Commit `feat: add inheritable theme profiles`.

### Task 3: Frontend runtime theme service

**Files:**
- Create: `monodoo_theme/static/src/theme/theme_service.js`
- Create: `monodoo_theme/static/src/theme/theme.scss`
- Create: `monodoo_theme/static/tests/theme_service.test.js`
- Modify: `tests/test_repository_contract.py`

**Interfaces:**
- Produces JS: `resolveThemeMode(preference, prefersDark) -> "light" | "dark"`
- Produces JS: `applyThemeContext(context, root, prefersDark) -> resolvedMode`
- Registers service: `monodoo_theme`
- Consumes RPC: `res.users.get_monodoo_theme_context()`

- [ ] Add failing repository-contract assertions for backend/unit-test asset declarations and frontend source files.
- [ ] Run repository-contract tests and confirm failure.
- [ ] Write HOOT tests first for explicit light/dark, system preference, CSS variable application, and theme data attributes.
- [ ] Implement minimal pure JS helpers and Odoo service using the standard `orm` service.
- [ ] Add conservative SCSS that defines fallbacks and themes only global surfaces/control-panel/navbar/buttons through semantic variables.
- [ ] Run Python contracts locally; the HOOT test is verified by the existing runtime CI once the branch is pushed.
- [ ] Commit `feat: apply monodoo themes at runtime`.

### Task 4: Runtime installation gate and documentation

**Files:**
- Modify: `README.md`
- Modify: `tests/runtime/prepare_database.sh`
- Modify: `tests/test_repository_contract.py`

**Interfaces:**
- Runtime database installs/upgrades `monodoo_theme` alongside existing addons.
- Documentation explains hierarchy, company/user resolution order, and companion-theme extension pattern without FACODI coupling.

- [ ] Add failing contract assertions that runtime install/upgrade commands include `monodoo_theme`.
- [ ] Run repository-contract tests and confirm failure.
- [ ] Update runtime installation/upgrade lists and README architecture/usage documentation.
- [ ] Run all local unittests with `python -m unittest discover -s tests -p 'test_*.py' -v`.
- [ ] Generate a diff and inspect for FACODI coupling, controller additions, navbar/webclient replacement, or accidental `monodoo_home` dependency changes.
- [ ] Commit `docs: document monodoo theme hierarchy`.
