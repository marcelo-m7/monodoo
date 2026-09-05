# Monodoo Home Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Use TDD for every behavior change and verification-before-completion before any success claim.

**Goal:** Build `monodoo_core` and `monodoo_home` for Odoo 19 Community so neutral `/odoo` opens a native application launcher while valid deep links, Odoo permissions, standard navigation, and fail-open behavior remain intact.

**Architecture:** `monodoo_core` is a deliberately minimal generic base addon. `monodoo_home` registers a standard root `ir.ui.menu` bound to an Owl `ir.actions.client`, reads permitted applications from Odoo's existing menu service, and applies one isolated patch to `WebClient._loadDefaultApp()` so only the no-state fallback selects Home. The launcher never queries `ir.ui.menu` independently and never replaces `/odoo`, authentication, the navbar, or Odoo's ACL model.

**Tech Stack:** Odoo 19 Community, Python manifests/XML data, Owl, Odoo web registries/services, HOOT, Docker/PostgreSQL, Playwright/pytest, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-05-monodoo-home-design.md`

## Global Constraints

- Odoo 19 Community only for v1.
- Versions: `monodoo_core=19.0.1.0.0`, `monodoo_home=19.0.1.0.0`.
- License: LGPL-3.
- `monodoo_core` depends only on `base`.
- `monodoo_home` depends exactly on `web` and `monodoo_core`.
- No FACODI dependency or behavior in Monodoo.
- No custom `/odoo` controller/redirect.
- No navbar replacement/patch.
- Home is a standard root menu for `base.group_user`, bound to `ir.actions.client`.
- Cards come only from `menuService.getApps()`, preserve Odoo order, exclude Home itself.
- Card navigation uses `menuService.selectMenu(app)`.
- Search is local and produces no RPC/fetch request.
- Default-home failure delegates to original Odoo `_loadDefaultApp()`.
- Browser/frontend verification is mandatory before release.
- `facodi-deploy` integration is a separate follow-up after Monodoo is merged and green.

## Target Files

```text
monodoo/
├── LICENSE
├── README.md
├── .github/workflows/ci.yml
├── docs/superpowers/specs/2026-09-05-monodoo-home-design.md
├── docs/superpowers/plans/2026-09-05-monodoo-home-implementation.md
├── tests/
│   ├── __init__.py
│   ├── test_repository_contract.py
│   ├── requirements.txt
│   ├── runtime/
│   │   ├── docker-compose.yml
│   │   ├── prepare_database.sh
│   │   └── wait_http.py
│   └── e2e/
│       ├── __init__.py
│       ├── conftest.py
│       ├── helpers.py
│       ├── test_home.py
│       └── test_hoot.py
├── monodoo_core/
│   ├── __init__.py
│   └── __manifest__.py
└── monodoo_home/
    ├── __init__.py
    ├── __manifest__.py
    ├── data/home_action.xml
    └── static/
        ├── src/
        │   ├── home/
        │   │   ├── constants.js
        │   │   ├── home.js
        │   │   ├── home.xml
        │   │   └── home.scss
        │   └── webclient/default_home.js
        └── tests/
            ├── home.test.js
            └── default_home.test.js
```

No Python model package is needed in v1.

---

## Task 0 — Start an isolated implementation branch

- [ ] Update `main` and require a clean tree:

```bash
git fetch origin
git checkout main
git pull --ff-only origin main
git status --short
```

Expected: no output from `git status --short`.

- [ ] Create:

```bash
git checkout -b feat/community-home
```

All implementation commits remain on this branch until PR merge.

---

## Task 1 — Repository contract and minimal installable addons

**Create:** `LICENSE`, `README.md`, `tests/__init__.py`, `tests/test_repository_contract.py`, both addon `__init__.py` and `__manifest__.py` files.

- [ ] Write `tests/test_repository_contract.py` first:

```python
from __future__ import annotations

import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
ADDONS = ("monodoo_core", "monodoo_home")


def load_manifest(addon: str) -> dict:
    return ast.literal_eval((ROOT / addon / "__manifest__.py").read_text(encoding="utf-8"))


class RepositoryContractTest(unittest.TestCase):
    def test_expected_addons_exist(self):
        for addon in ADDONS:
            self.assertTrue((ROOT / addon / "__manifest__.py").is_file())
            self.assertTrue((ROOT / addon / "__init__.py").is_file())

    def test_versions_license_installability(self):
        for addon in ADDONS:
            manifest = load_manifest(addon)
            self.assertEqual(manifest["version"], "19.0.1.0.0")
            self.assertEqual(manifest["license"], "LGPL-3")
            self.assertTrue(manifest["installable"])
            self.assertFalse(manifest["application"])

    def test_dependency_boundary(self):
        self.assertEqual(load_manifest("monodoo_core")["depends"], ["base"])
        self.assertEqual(load_manifest("monodoo_home")["depends"], ["web", "monodoo_core"])

    def test_no_facodi_coupling(self):
        for addon in ADDONS:
            for path in (ROOT / addon).rglob("*"):
                if path.is_file() and path.suffix in {".py", ".js", ".xml", ".scss"}:
                    self.assertNotIn("facodi", path.read_text(encoding="utf-8").lower(), str(path))

    def test_no_controller_package(self):
        for addon in ADDONS:
            self.assertFalse((ROOT / addon / "controllers").exists())


if __name__ == "__main__":
    unittest.main()
```

- [ ] Verify RED:

```bash
python3 -m unittest tests.test_repository_contract -v
```

Expected: missing addon manifests.

- [ ] Create `monodoo_core/__manifest__.py`:

```python
{
    "name": "Monodoo Core",
    "summary": "Shared technical base for Monodoo Community capabilities",
    "version": "19.0.1.0.0",
    "category": "Technical",
    "license": "LGPL-3",
    "depends": ["base"],
    "installable": True,
    "application": False,
}
```

- [ ] Create `monodoo_home/__manifest__.py` with no data/assets yet, so Task 1 is internally installable:

```python
{
    "name": "Monodoo Home",
    "summary": "Native Community application launcher for Odoo 19",
    "version": "19.0.1.0.0",
    "category": "Productivity",
    "license": "LGPL-3",
    "depends": ["web", "monodoo_core"],
    "installable": True,
    "application": False,
}
```

Both `__init__.py` files stay empty. Add standard LGPL-3 text and a README stating Odoo 19 Community support and repository boundaries.

- [ ] Verify GREEN:

```bash
python3 -m unittest tests.test_repository_contract -v
```

- [ ] Commit:

```bash
git add LICENSE README.md tests monodoo_core monodoo_home
git commit -m "feat: establish Monodoo addon foundation"
```

---

## Task 2 — Standard Home action, root menu, launcher, and local search

**Create:** `data/home_action.xml`, `static/src/home/{constants.js,home.js,home.xml,home.scss}`, `static/tests/home.test.js`.
**Modify:** `monodoo_home/__manifest__.py`, repository contract.

- [ ] Extend repository contract first to require parsed XML, IDs, and Task-2 manifest entries. Verify RED.

Required final Task-2 manifest additions:

```python
"data": ["data/home_action.xml"],
"assets": {
    "web.assets_backend": ["monodoo_home/static/src/home/**/*"],
    "web.assets_unit_tests": ["monodoo_home/static/tests/**/*.test.js"],
},
```

- [ ] Create `home_action.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="action_monodoo_home" model="ir.actions.client">
        <field name="name">Home</field>
        <field name="tag">monodoo_home</field>
    </record>
    <menuitem
        id="menu_monodoo_home"
        name="Home"
        action="action_monodoo_home"
        sequence="1"
        groups="base.group_user"
    />
</odoo>
```

- [ ] Create `constants.js`:

```javascript
export const MONODOO_HOME_MENU_XMLID = "monodoo_home.menu_monodoo_home";
```

- [ ] Write failing HOOT behavior in `home.test.js` using Odoo's `defineMenus`, `defineActions`, `mountWithCleanup`, `contains`, `getService`, `useTestClientAction`, and `queryAllTexts`. Tests must prove:
  - order `CRM`, `Project` is preserved;
  - Home is excluded;
  - Odoo `webIconData` is used and missing icons get a neutral fallback;
  - typing `pro` leaves only `Project`;
  - selecting the first card makes CRM the current app via the menu service;
  - Home-only input renders `.o_monodoo_empty`;
  - typing into search after mount triggers no XHR/fetch.

Representative core assertion:

```javascript
expect(queryAllTexts(".o_monodoo_app_name")).toEqual(["CRM", "Project"]);
```

- [ ] Implement `home.js`:

```javascript
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, useState } from "@odoo/owl";
import { MONODOO_HOME_MENU_XMLID } from "./constants";

export class MonodooHome extends Component {
    static template = "monodoo_home.Home";
    static props = ["*"];

    setup() {
        this.menuService = useService("menu");
        this.state = useState({ query: "" });
    }

    get apps() {
        const query = this.state.query.trim().toLocaleLowerCase();
        const apps = this.menuService
            .getApps()
            .filter((app) => app.xmlid !== MONODOO_HOME_MENU_XMLID);
        return query
            ? apps.filter((app) => (app.name || "").toLocaleLowerCase().includes(query))
            : apps;
    }

    openApp(app) {
        return this.menuService.selectMenu(app);
    }
}

registry.category("actions").add("monodoo_home", MonodooHome);
```

- [ ] Implement `home.xml` as one Odoo-native view: heading `Applications`, search input `.o_monodoo_search`, responsive ordered card grid `.o_monodoo_app_card`, Odoo icon `.o_app_icon`, `oi oi-apps` fallback, and `.o_monodoo_empty` state. No custom color palette.

- [ ] `home.scss` only sets neutral sizing:

```scss
.o_monodoo_home_inner { max-width: 1100px; }
.o_monodoo_app_card {
    min-height: 7rem;
    .o_app_icon { width: 3rem; height: 3rem; object-fit: contain; }
}
```

- [ ] Run contract tests and verify GREEN:

```bash
python3 -m unittest tests.test_repository_contract -v
```

- [ ] Commit:

```bash
git add monodoo_home tests/test_repository_contract.py
git commit -m "feat: add Community application launcher"
```

---

## Task 3 — Neutral `/odoo` automatic Home with fail-open fallback

**Create:** `static/src/webclient/default_home.js`, `static/tests/default_home.test.js`.
**Modify:** manifest and repository contract.

- [ ] Write failing HOOT helper tests proving Home selection, missing-Home fallback, failed-selection fallback, and no-state `WebClient` startup rendering `.o_monodoo_home`.

Core helper tests use:

```javascript
import { MONODOO_HOME_MENU_XMLID } from "@monodoo_home/home/constants";
import { loadMonodooDefaultApp } from "@monodoo_home/webclient/default_home";
```

- [ ] Implement `default_home.js`:

```javascript
import { patch } from "@web/core/utils/patch";
import { WebClient } from "@web/webclient/webclient";
import { MONODOO_HOME_MENU_XMLID } from "@monodoo_home/home/constants";

export async function loadMonodooDefaultApp(menuService, fallback) {
    const homeMenu = menuService
        .getApps()
        .find((app) => app.xmlid === MONODOO_HOME_MENU_XMLID);
    if (!homeMenu) {
        return fallback();
    }
    try {
        return await menuService.selectMenu(homeMenu);
    } catch (error) {
        console.warn("Monodoo Home failed to load; using Odoo default app", error);
        return fallback();
    }
}

patch(WebClient.prototype, {
    _loadDefaultApp() {
        return loadMonodooDefaultApp(this.menuService, () => super._loadDefaultApp());
    },
});
```

Do not patch `loadRouterState()`.

- [ ] Add the new backend asset, producing final list:

```python
"web.assets_backend": [
    "monodoo_home/static/src/home/**/*",
    "monodoo_home/static/src/webclient/default_home.js",
],
```

- [ ] Strengthen static contract: exactly one `patch(WebClient.prototype` under Monodoo, no `patch(NavBar`, no `t-inherit="web.NavBar"`, no controller package.

- [ ] Verify contract GREEN and commit:

```bash
python3 -m unittest tests.test_repository_contract -v
git add monodoo_home tests/test_repository_contract.py
git commit -m "feat: open Monodoo Home on neutral backend entry"
```

---

## Task 4 — Real Odoo 19 runtime, HOOT gate, and browser acceptance

**Create:** runtime files and `tests/e2e` package.

- [ ] Pin `tests/requirements.txt`:

```text
playwright==1.55.0
pytest==8.4.2
```

Resolve and commit an exact replacement pin only if the configured package index proves one of these versions unavailable.

- [ ] Create `tests/runtime/docker-compose.yml`:

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: postgres
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: odoo
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U odoo -d postgres"]
      interval: 2s
      timeout: 2s
      retries: 30
  odoo:
    image: odoo:19.0
    depends_on:
      db:
        condition: service_healthy
    ports: ["8069:8069"]
    environment:
      HOST: db
      USER: odoo
      PASSWORD: odoo
    volumes:
      - ../..:/mnt/extra-addons:ro
    command:
      - --database=monodoo_test
      - --db-filter=^monodoo_test$
      - --without-demo=all
      - --workers=0
      - --max-cron-threads=0
```

- [ ] Create `wait_http.py` using only stdlib: poll URL once/sec until status `<500`, timeout with non-zero exit and last exception.

- [ ] Create `prepare_database.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

docker compose down -v --remove-orphans
docker compose up -d db

docker compose run --rm odoo \
  --database=monodoo_test --stop-after-init --without-demo=all \
  -i monodoo_core,monodoo_home,crm,project

cat <<'PY' | docker compose run --rm -T odoo shell -d monodoo_test
admin = env.ref("base.user_admin")
admin.password = "admin"
internal_group = env.ref("base.group_user")
project_group = env.ref("project.group_project_user")
login = "project.user@example.test"
user = env["res.users"].search([("login", "=", login)], limit=1)
vals = {
    "name": "Project User",
    "login": login,
    "password": "project",
    "group_ids": [(6, 0, [internal_group.id, project_group.id])],
}
(user.write(vals) if user else env["res.users"].create(vals))
env.cr.commit()
PY

docker compose run --rm odoo \
  --database=monodoo_test --stop-after-init --without-demo=all \
  -u monodoo_core,monodoo_home

docker compose up -d odoo
python3 wait_http.py http://127.0.0.1:8069/web/login 90
```

`group_ids` is the Odoo 19 `res.users` field; do not broaden the restricted user's groups. CRM root is restricted to Sales groups, while Project is granted through `project.group_project_user`.

- [ ] Create `tests/e2e/helpers.py`:

```python
from playwright.sync_api import Page

BASE_URL = "http://127.0.0.1:8069"


def login(page: Page, login_name: str, password: str) -> None:
    page.goto(f"{BASE_URL}/web/login")
    page.locator("input[name='login']").fill(login_name)
    page.locator("input[name='password']").fill(password)
    page.locator("button[type='submit']").click()
    page.wait_for_load_state("networkidle")
```

- [ ] Create `conftest.py` with a session Chromium fixture and per-test page/context fixture. Collect `pageerror` events, always close context in `finally`, and fail after the test if page errors occurred.

- [ ] Create `test_home.py` with these exact behavioral gates:
  1. admin login + neutral `/odoo` -> `.o_monodoo_home` visible and >1 business card;
  2. click CRM, capture resulting deep-link URL, reload that URL -> Home absent;
  3. local `Project` search leaves one Project card and does not increase XHR/fetch count after network idle;
  4. desktop standard Apps dropdown contains Home and selecting it returns Home;
  5. restricted project user sees Project and does not see CRM;
  6. 390×844 standard mobile app sidebar exposes Home and selecting it returns Home.

Use selectors from exact Odoo 19 DOM. Selector fixes are allowed; behavioral assertions are not.

- [ ] Create `test_hoot.py`. Odoo 19's own `WebSuite` runs `/web/tests?headless&loglevel=2&preset=desktop&timeout=15000` and treats console signal `[HOOT] Test suite succeeded` as success. Mirror that contract:

```python
from tests.e2e.helpers import BASE_URL, login


def test_hoot_suite_succeeds(page):
    login(page, "admin", "admin")
    hoot_failures: list[str] = []
    page.on(
        "console",
        lambda message: hoot_failures.append(message.text)
        if "[HOOT]" in message.text and "failed" in message.text.lower()
        else None,
    )
    with page.expect_console_message(
        predicate=lambda message: "[HOOT] Test suite succeeded" in message.text,
        timeout=3_600_000,
    ):
        page.goto(
            f"{BASE_URL}/web/tests?headless&loglevel=2&preset=desktop&timeout=15000",
            wait_until="domcontentloaded",
        )
    assert not hoot_failures
```

This runs the installed `web.assets_unit_tests`, which includes the Monodoo `.test.js` files declared by the addon.

- [ ] Run clean local acceptance:

```bash
python3 -m venv .venv-test
. .venv-test/bin/activate
pip install -r tests/requirements.txt
python -m playwright install chromium
chmod +x tests/runtime/prepare_database.sh tests/runtime/wait_http.py
tests/runtime/prepare_database.sh
pytest tests/e2e -q
```

Expected: install, upgrade, HOOT, desktop, mobile, permissions, and deep-link gates all PASS.

- [ ] Tear down and commit:

```bash
cd tests/runtime && docker compose down -v --remove-orphans && cd ../..
git add tests
git commit -m "test: add Odoo 19 runtime acceptance harness"
```

---

## Task 5 — GitHub Actions release gates

**Create:** `.github/workflows/ci.yml`.
**Modify:** `README.md`.

- [ ] Create workflow:

```yaml
name: CI
on:
  push:
  pull_request:

jobs:
  repository-contract:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: "3.12"}
      - run: python -m unittest tests.test_repository_contract -v

  odoo-runtime:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: "3.12"}
      - run: pip install -r tests/requirements.txt
      - run: python -m playwright install --with-deps chromium
      - run: chmod +x tests/runtime/prepare_database.sh tests/runtime/wait_http.py
      - run: tests/runtime/prepare_database.sh
      - run: pytest tests/e2e -q
      - if: always()
        run: cd tests/runtime && docker compose logs --no-color
      - if: always()
        run: cd tests/runtime && docker compose down -v --remove-orphans
```

- [ ] README documents exact local verification commands and `http://localhost:8069/odoo`.

- [ ] Run locally before push, then commit:

```bash
git add .github/workflows/ci.yml README.md
git commit -m "ci: validate Monodoo Home on Odoo 19"
git push -u origin feat/community-home
```

- [ ] Record the workflow run ID and inspect every job conclusion. Do not call the branch green unless every required job is `success`.

---

## Task 6 — Final verification, PR, merge, post-merge evidence

- [ ] From a clean environment run:

```bash
python3 -m unittest tests.test_repository_contract -v
rm -rf .venv-test
python3 -m venv .venv-test
. .venv-test/bin/activate
pip install -r tests/requirements.txt
python -m playwright install chromium
tests/runtime/prepare_database.sh
pytest tests/e2e -q
```

- [ ] Explicitly map all 19 spec acceptance criteria to automated evidence/static inspection.

Static invariants:

```bash
grep -R "facodi" monodoo_core monodoo_home && exit 1 || true
grep -R "patch(NavBar\|t-inherit=\"web.NavBar\"" monodoo_home && exit 1 || true
test ! -d monodoo_home/controllers
test ! -d monodoo_core/controllers
test "$(grep -R "patch(WebClient.prototype" -l monodoo_home | wc -l)" -eq 1
```

- [ ] Re-check exact Odoo 19 upstream contracts immediately before PR: no-state-only `_loadDefaultApp()`, `getApps()` root children, `selectMenu()` standard action/current-menu synchronization, standard desktop/mobile app navigation.

- [ ] Open PR titled:

```text
Add Odoo 19 Community Home launcher
```

PR body includes module boundaries, root-menu/client-action design, isolated fallback patch, permission model, local/CI evidence + run IDs, and explicit statement that `facodi-deploy` is unchanged.

- [ ] Merge only after PR CI is fully `success`.

- [ ] Fetch resulting `main` SHA and post-merge workflow run. Only then call Monodoo v1 independently green.

## Separate Follow-up Gate — `facodi-deploy`

Do not implement deployment integration under this plan. Once Monodoo has a merged, post-merge-green `main` SHA, write a separate plan using that exact SHA to: add `addons/monodoo` as a pinned submodule, add `monodoo_core,monodoo_home` to `FACODI_MODULES`, verify nested-addon Docker discovery, extend authenticated `/odoo` acceptance, confirm Website/eLearning/deep links remain unchanged, and merge only after canonical Coolify/runtime acceptance is green.
