# Monodoo Home — Odoo 19 Community Design

Date: 2026-09-05
Status: Approved design, pending implementation plan
Repository: `marcelo-m7/monodoo`
Target: Odoo 19 Community
License: LGPL-3

## 1. Purpose

Monodoo is a reusable configuration layer for Odoo Community instances. Its first capability is an authenticated backend home at `/odoo`, presented after login when there is no explicit action or deep link to restore.

The first release deliberately solves one concrete problem only: provide a native, neutral application launcher for Odoo 19 Community without replacing the webclient, authentication, menu security, routing, or standard navigation.

The design must remain generic. Nothing in `monodoo_core` or `monodoo_home` may depend on FACODI.

## 2. Scope

### In scope for v1

- Odoo 19 Community support.
- Automatic Home after internal user login when `/odoo` has no valid action/state.
- Preserve valid deep links and restored actions.
- Render all root applications already allowed to the current user.
- Preserve Odoo application ordering.
- Use the application name and icon already exposed by Odoo's menu service.
- Local frontend search by application name.
- Open applications using the standard Odoo menu/action service.
- Keep the standard desktop apps dropdown available.
- Add a Home entry to the apps navigation so users can return to the launcher.
- Preserve the standard mobile apps flow.
- Fail open to the original Odoo default-app behavior if Monodoo Home cannot load.
- Clean install and upgrade support.
- CI verification against a real Odoo 19 Community runtime.

### Explicitly out of scope for v1

- Odoo 17/18/20 compatibility.
- Enterprise pixel-perfect cloning.
- Favorites, recents, badges, KPIs, widgets, drag and drop, or user-customizable dashboards.
- Per-user or administrator-maintained application catalogs.
- A second ACL/security model.
- Custom `/odoo` HTTP controllers or redirects.
- Authentication changes.
- A generic YAML/profile engine.
- Automated company, mail, website, security, or branding configuration.
- FACODI-specific behavior.

## 3. Architectural approach

The implementation uses two Odoo addons in one repository:

```text
monodoo/
├── monodoo_core/
└── monodoo_home/
```

### `monodoo_core`

`monodoo_core` is intentionally small in v1. It establishes the Monodoo namespace and common extension boundary for future capabilities, without prematurely introducing a generic configurator engine.

Responsibilities:

- Monodoo identity and versioning.
- Capability namespace / common extension points where genuinely needed.
- Shared technical base for future Monodoo addons.

It must not introduce unused models, configuration DSLs, queues, generic installers, or instance profiles in v1.

### `monodoo_home`

`monodoo_home` depends on `web` and `monodoo_core`.

Responsibilities:

- Register the Home client action.
- Render the application launcher as an Owl component.
- Read the allowed root applications through Odoo's existing menu service.
- Filter applications locally for search.
- Open applications using the standard menu/action service.
- Integrate Home into the standard apps navigation.
- Adapt the default-app fallback so the neutral `/odoo` route opens Monodoo Home.
- Delegate back to Odoo's original fallback if Monodoo Home fails.

## 4. Odoo integration points

The design intentionally relies on a small number of existing Odoo 19 webclient mechanisms.

### 4.1 Default route behavior

Odoo 19 `WebClient.loadRouterState()` attempts to restore the current action/state. If no state is loaded, it calls `_loadDefaultApp()`. The standard `_loadDefaultApp()` selects the first root application.

Monodoo changes only this fallback path.

Expected behavior:

```text
login/internal navigation
        |
        v
      /odoo
        |
        v
Odoo tries to restore valid state/action
        |
        +-- state/action exists --> preserve standard Odoo behavior
        |
        +-- no valid state -------> Monodoo Home client action
```

The adapter must be isolated in a small frontend file so an Odoo 20 migration has one obvious compatibility boundary to review.

### 4.2 Application source

The Odoo 19 menu service already exposes `getApps()`, which returns the children of the root menu after Odoo has loaded menus for the current user.

Monodoo must use this service rather than querying `ir.ui.menu` independently.

Consequences:

- No duplicated ACL logic.
- No `sudo()` menu lookup.
- New authorized applications appear automatically.
- Applications the user cannot access do not appear.
- Odoo's own application ordering is preserved.

### 4.3 Opening an application

App cards must open applications through the standard menu service, using the equivalent of `menuService.selectMenu(app)` rather than manually constructing URLs or dispatching arbitrary actions.

This preserves Odoo's action behavior, breadcrumbs, current-app state, and menu synchronization.

### 4.4 Apps navigation

The standard apps dropdown remains available on desktop. Monodoo must not turn the existing apps button into a replacement Home-only button.

Instead, Home is exposed as an additional first-class destination in the apps navigation. On mobile, the existing `/odoo` / all-apps behavior should continue to lead naturally to the Monodoo Home when no explicit action is present.

## 5. User experience

The v1 visual language is Odoo-native and neutral.

### Layout

```text
+------------------------------------------------------+
| Odoo / standard navbar                  user / tray  |
+------------------------------------------------------+
|                                                      |
|                    Applications                      |
|                                                      |
|              [ Search applications... ]              |
|                                                      |
|   [icon] CRM   [icon] Sales   [icon] Project   ...   |
|                                                      |
+------------------------------------------------------+
```

### Card data

Each card contains only:

- Odoo-provided application icon when available.
- Application name.

No badges, descriptions, metrics, shortcuts, custom categories, or Monodoo branding in v1.

### Search

Search is purely client-side against the application list already loaded in memory. It must not trigger extra RPC calls.

The default ordering is never replaced by alphabetical sorting.

### Empty state

If the user has no root applications, the Home renders a clear neutral empty state instead of crashing.

### Missing icon

An application without an icon must still render predictably using an Odoo-compatible neutral fallback.

## 6. Failure behavior

The feature is fail-open to standard Odoo behavior.

If Monodoo Home cannot be resolved or executed during the default-app fallback, the adapter must invoke the original Odoo default-app behavior and allow the first permitted application to open.

This rule is critical: installing `monodoo_home` must never make the backend inaccessible merely because the custom launcher fails.

The implementation must not override `/odoo` at the controller level and must not alter login/session mechanics.

## 7. Proposed repository structure

```text
monodoo/
├── README.md
├── docs/
│   └── superpowers/
│       └── specs/
│           └── 2026-09-05-monodoo-home-design.md
├── tests/
│   └── repository_contract.py
├── monodoo_core/
│   ├── __init__.py
│   ├── __manifest__.py
│   └── ...
└── monodoo_home/
    ├── __init__.py
    ├── __manifest__.py
    ├── data/
    │   └── client_action.xml
    ├── static/src/
    │   ├── home/
    │   │   ├── home.js
    │   │   ├── home.xml
    │   │   └── home.scss
    │   └── webclient/
    │       └── default_home.js
    └── tests/
```

Exact filenames may be adjusted during implementation if Odoo's native 19.0 patterns make a different location more appropriate, but the responsibility boundaries above must remain intact.

## 8. Versioning and licensing

Initial module versions:

```text
monodoo_core  19.0.1.0.0
monodoo_home  19.0.1.0.0
```

License: LGPL-3.

Odoo 19 is the only supported runtime in the first release. The code should be structured to make later version branches or adapters possible, but no compatibility abstraction for versions not yet implemented should be added now.

## 9. Acceptance criteria

The release is accepted only when all of the following are proven:

1. Odoo 19 Community clean install succeeds.
2. Upgrade of `monodoo_core` and `monodoo_home` succeeds.
3. Internal login followed by neutral `/odoo` opens Monodoo Home.
4. A valid Odoo deep link still opens its target action rather than Home.
5. All root applications allowed to the user appear.
6. Applications not allowed to the user do not appear.
7. Application order matches Odoo's own menu order.
8. Application icons come from Odoo menu data where available.
9. Search works locally without an additional RPC.
10. Clicking an application opens it through the standard Odoo menu/action mechanism.
11. The standard desktop apps dropdown remains functional.
12. Home remains reachable from apps navigation after opening another app.
13. Standard mobile app navigation remains functional.
14. No custom controller replaces or shadows `/odoo`.
15. A Monodoo Home bootstrap failure falls back to Odoo's original default-app behavior.
16. Assets compile and the webclient starts without JS/Owl errors.
17. The addons have no FACODI-specific dependency or behavior.

## 10. Test strategy

### 10.1 Repository contract tests

Fast checks on every commit:

- Python/manifest syntax.
- XML parseability.
- `monodoo_home` depends on `web` and `monodoo_core`.
- No FACODI dependencies.
- No custom `/odoo` controller.
- Asset declarations exist and point to real files.
- Module versions use the Odoo 19 version prefix.
- LGPL-3 metadata is present.

### 10.2 Frontend tests

Cover at minimum:

- App list from menu service.
- Card rendering.
- Application without icon.
- Empty application list.
- Local search/filtering.
- Selection via standard menu service.
- Home navigation entry.
- Default-app fallback.
- Fallback to original Odoo behavior on Home failure.

### 10.3 Odoo 19 integration tests

CI should start PostgreSQL plus an Odoo 19 Community runtime and verify:

```text
fresh database
  -> install monodoo_core
  -> install monodoo_home
  -> compile/load assets
  -> authenticate internal user
  -> neutral /odoo opens Home
  -> open application from Home
  -> verify valid deep link
  -> verify permissions with restricted user
  -> upgrade modules
```

A green Python/XML install alone is insufficient because the main feature lives in the webclient.

## 11. Future capability direction

The architecture intentionally leaves space for later independent addons, for example:

```text
monodoo_core
├── monodoo_home
├── monodoo_branding
├── monodoo_instance_profile
├── monodoo_company_setup
├── monodoo_mail_setup
├── monodoo_website_setup
├── monodoo_security_baseline
└── monodoo_module_sets
```

These are not part of the v1 implementation plan. Each future capability should be designed when its real requirements are known.

## 12. FACODI deployment integration

`facodi-deploy` must consume Monodoo only after the Monodoo release is independently merged and green.

Target integration:

```text
facodi-deploy
└── addons/
    ├── facodi-learning
    ├── facodi-theme
    ├── facodi-ai
    ├── monynha-odoo
    └── monodoo
```

The deployment repository will add `monodoo` as a git submodule. Its current Docker build already discovers addon manifests using the nested `addons/<repository>/<addon>/__manifest__.py` pattern, which is compatible with `addons/monodoo/monodoo_core` and `addons/monodoo/monodoo_home`.

After the Monodoo release is green, `facodi-deploy` should add both module names to its migration/install list and extend its runtime acceptance test so `/odoo` after authentication verifies the Community Home behavior.

No Monodoo code should be copied into `facodi-deploy`; that repository should only pin and install the independently versioned Monodoo source.

## 13. Source references used for the design

The design is based on Odoo 19 Community's standard webclient behavior, especially:

- `addons/web/static/src/webclient/webclient.js`: `loadRouterState()` and `_loadDefaultApp()`.
- `addons/web/static/src/webclient/menus/menu_service.js`: `getApps()`, `selectMenu()`, `setCurrentMenu()`.
- `addons/web/static/src/webclient/navbar/navbar.xml`: standard applications dropdown and mobile all-apps navigation.

These integration points must be re-verified against the exact Odoo 19 source used by CI before implementation is finalized.
