# Monodoo Navigation — Odoo 19 Community Design

Date: 2026-09-07
Status: Approved
Repository: `marcelo-m7/monodoo`
Target: Odoo 19 Community
License: LGPL-3

## Purpose

Phase 2 evolves Monodoo from a launcher plus theme engine into a reusable Odoo-native backend navigation layer. It adds a modular applications sidebar and enriches Monodoo Home with favorites and recent applications without replacing Odoo routing, menu security, or action handling.

## Modules

### `monodoo_appsbar`

A standalone addon depending on `web` and `monodoo_core`.

Responsibilities:

- render an application sidebar inside the standard Odoo WebClient;
- source root applications exclusively from the existing menu service;
- preserve Odoo application ordering and authorization;
- open applications through `menuService.selectMenu(app)`;
- highlight the current application;
- provide per-user sidebar modes: `auto`, `expanded`, `compact`, `hidden`;
- keep standard Odoo navbar and mobile navigation available;
- hide the sidebar on small/mobile screens in `auto` mode;
- expose no second menu/ACL model.

`monodoo_appsbar` must remain installable without `monodoo_theme`. When the theme addon is installed it naturally consumes the shared CSS custom properties, but it must have neutral fallbacks.

### `monodoo_home` evolution

The existing Home remains the default neutral `/odoo` fallback and continues using the menu service. Phase 2 adds:

- favorites backed by the current user's preferences;
- recent applications stored client-side and namespaced by database/user;
- sections for Favorites, Recent, and All applications;
- a favorite toggle on application cards;
- existing local application search across the authorized app list;
- no extra search RPCs.

The Home root menu itself is never shown as a business application, favorite, or recent entry.

## Persistence

### Favorites

`res.users.monodoo_favorite_app_xmlids` stores a JSON list of root application XML IDs. It is self-readable and self-writeable, because it is only a presentation preference. Server methods sanitize values against root apps available to the current user before returning effective favorites.

### Recents

Recent app XML IDs are stored in browser `localStorage`. Storage keys include database and user identity so different users/databases do not share history. The list is bounded to six unique entries, most recent first.

## AppsBar layout

- `expanded`: 13rem sidebar with icon + application name.
- `compact`: 4rem sidebar with icon and accessible tooltip/title.
- `hidden`: no sidebar.
- `auto`: expanded on wide desktops, compact on medium desktops/tablets, hidden below the mobile breakpoint.

The sidebar begins below the 46px Odoo navbar. The action manager receives matching left inset only while the sidebar is visible. The standard navbar is not replaced.

## Integration boundary

A small extension of `web.WebClient` registers and renders the AppsBar component after `NavBar`. This is the only WebClient template integration in `monodoo_appsbar`. No controller, authentication, router, `NavBar` replacement, or menu-service replacement is allowed.

## Failure behavior

- If favorites persistence fails, Home continues to open applications normally.
- If localStorage is unavailable, recents degrade to an in-memory empty list.
- If sidebar preference is unavailable, `auto` is used.
- Application selection always delegates to Odoo.

## Security

No `sudo()` is used to enumerate applications. Root applications always come from the menu service or from Odoo's menu tree for the current user. Favorite XML IDs are presentation metadata and never grant access.

## Testing

Release gates cover:

- addon/repository contracts;
- sidebar mode and self-preference model contracts;
- recent-list ordering/deduplication/bounds;
- favorite filtering/toggling behavior;
- HOOT rendering and standard menu-service selection;
- clean Odoo 19 Community install/upgrade with `monodoo_core`, `monodoo_home`, `monodoo_theme`, and `monodoo_appsbar`;
- existing launcher/deep-link behavior remains green.
