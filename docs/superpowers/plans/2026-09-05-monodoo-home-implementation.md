# Monodoo Home Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Use TDD for every behavior change and verification-before-completion before any success claim.

**Goal:** Build `monodoo_core` and `monodoo_home` for Odoo 19 Community so neutral `/odoo` opens a native application launcher while valid deep links, Odoo permissions, standard navigation, and fail-open behavior remain intact.

**Architecture:** `monodoo_core` is a deliberately minimal generic base addon. `monodoo_home` registers a standard root `ir.ui.menu` bound to an Owl `ir.actions.client`, reads permitted applications from Odoo's existing menu service, and applies one isolated patch to `WebClient._loadDefaultApp()` so only the no-state fallback selects Home. The launcher never queries `ir.ui.menu` independently and never replaces `/odoo`, authentication, the navbar, or Odoo's ACL model.

**Tech Stack:** Odoo 19 Community, Python manifests/XML data, Owl, Odoo web registries/services, HOOT frontend tests, Docker/PostgreSQL runtime validation, Playwright browser acceptance tests, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-05-monodoo-home-design.md`

## Global Constraints

- Target runtime is Odoo 19 Community only.
- Initial versions are exactly `19.0.1.0.0` for both `monodoo_core` and `monodoo_home`.
- License is LGPL-3.
- `monodoo_core` depends only on `base` in v1.
- `monodoo_home` depends exactly on `web` and `monodoo_core`.
- No FACODI dependency, naming, data model, URL, or runtime behavior may appear in either addon.
- Do not add compatibility abstractions for Odoo 17, 18, or 20.
- Do not create a custom `/odoo` controller or redirect.
- Do not patch or replace the standard navbar template.
- Home is a standard root `ir.ui.menu` available to `base.group_user` and bound to a standard `ir.actions.client`.
- Business application cards come only from `menuService.getApps()` and preserve Odoo order after filtering out Home itself.
- Opening an application uses `menuService.selectMenu(app)`.
- Search is local-only and must not trigger an RPC/fetch request.
- The default-home adapter must fail open to Odoo's original `_loadDefaultApp()` behavior.
- A green install without frontend/browser evidence is insufficient for release.
- `facodi-deploy` integration is a separate follow-up plan and must not begin until Monodoo is merged and independently green.

## Target File Structure

```text
monodoo/
├── LICENSE
├── README.md
├── .github/
│   └── workflows/
│       └── ci.yml
├── docs/
│   └── superpowers/
│       ├── specs/
│       │   └── 2026-09-05-monodoo-home-design.md
│       └── plans/
│           └── 2026-09-05-monodoo-home-implementation.md
├── tests/
│   ├── __init__.py
│   ├── test_repository_contract.py
│   ├── requirements.txt
│   ├── runtime/
│   │   ├── docker-compose.yml
│   │   ├── prepare_database.sh
│   │   └── wait_http.py
│   └── e2e/
│       ├── conftest.py
│       ├── test_home.py
│       └── test_hoot.py
├── monodoo_core/
│   ├── __init__.py
│   └── __manifest__.py
└── monodoo_home/
    ├── __init__.py
    ├── __manifest__.py
    ├── data/
    │   └── home_action.xml
    └── static/
        ├── src/
        │   ├── home/
        │   │   ├── constants.js
        │   │   ├── home.js
        │   │   ├── home.xml
        │   │   └── home.scss
        │   └── webclient/
        │       └── default_home.js
        └── tests/
            ├── home.test.js
            └── default_home.test.js
```

No Python model package is created in v1 because neither addon needs a custom business model.

---

### Task 0: Start implementation on an isolated branch

**Files:** none.

- [ ] **Step 1: Verify `main` still contains only approved planning artifacts**

Run:

```bash
git fetch origin
git checkout main
git pull --ff-only origin main
git status --short
```

Expected: clean working tree.

- [ ] **Step 2: Create the implementation branch**

```bash
git checkout -b feat/community-home
```

All implementation commits from Tasks 1-6 stay on this branch until PR merge.

---

### Task 1: Establish the repository contract and minimal installable addons

**Files:**
- Create: `LICENSE`
- Create: `README.md`
- Create: `tests/__init__.py`
- Create: `tests/test_repository_contract.py`
- Create: `monodoo_core/__init__.py`
- Create: `monodoo_core/__manifest__.py`
- Create: `monodoo_home/__init__.py`
- Create: `monodoo_home/__manifest__.py`

**Interfaces:** Produces two independently parseable Odoo 19 addon manifests. No XML/data/assets are declared yet, so this commit remains internally complete.

- [ ] **Step 1: Write the failing repository contract test**

Create `tests/test_repository_contract.py`:

```python
from __future__ import annotations

import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
ADDONS = ("monodoo_core", "monodoo_home")


def load_manifest(addon: str) -> dict:
    return ast.literal_eval(
        (ROOT / addon / "__manifest__.py").read_text(encoding="utf-8")
    )


class RepositoryContractTest(unittest.TestCase):
    def test_expected_addons_exist(self):
        for addon in ADDONS:
            self.assertTrue((ROOT / addon / "__manifest__.py").is_file())
            self.assertTrue((ROOT / addon / "__init__.py").is_file())

    def test_versions_license_and_installability(self):
        for addon in ADDONS:
            manifest = load_manifest(addon)
            self.assertEqual(manifest["version"], "19.0.1.0.0")
            self.assertEqual(manifest["license"], "LGPL-3")
            self.assertTrue(manifest["installable"])
            self.assertFalse(manifest["application"])

    def test_dependency_boundary(self):
        self.assertEqual(load_manifest("monodoo_core")["depends"], ["base"])
        self.assertEqual(
            load_manifest("monodoo_home")["depends"],
            ["web", "monodoo_core"],
        )

    def test_no_facodi_coupling(self):
        for addon in ADDONS:
            for path in (ROOT / addon).rglob("*"):
                if path.is_file() and path.suffix in {".py", ".js", ".xml", ".scss"}:
                    content = path.read_text(encoding="utf-8").lower()
                    self.assertNotIn("facodi", content, str(path))

    def test_no_controller_package(self):
        for addon in ADDONS:
            self.assertFalse((ROOT / addon / "controllers").exists())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test and verify RED**

```bash
python3 -m unittest tests.test_repository_contract -v
```

Expected: FAIL because the addon directories/manifests do not exist.

- [ ] **Step 3: Create minimal manifests**

`monodoo_core/__manifest__.py`:

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

`monodoo_home/__manifest__.py`:

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

Both `__init__.py` files are empty. Do not add unused models/hooks.

Add the standard LGPL-3 text to `LICENSE`. `README.md` states Odoo 19 Community support, LGPL-3, the two modules, and explicitly says FACODI deployment integration belongs to its deployment repository.

- [ ] **Step 4: Run the contract test and verify GREEN**

```bash
python3 -m unittest tests.test_repository_contract -v
```

Expected: PASS.

- [ ] **Step 5: Commit Task 1**

```bash
git add LICENSE README.md tests monodoo_core monodoo_home
git commit -m "feat: establish Monodoo addon foundation"
```

---

### Task 2: Implement the standard Home action, root menu, and launcher

**Files:**
- Create: `monodoo_home/data/home_action.xml`
- Create: `monodoo_home/static/src/home/constants.js`
- Create: `monodoo_home/static/src/home/home.js`
- Create: `monodoo_home/static/src/home/home.xml`
- Create: `monodoo_home/static/src/home/home.scss`
- Create: `monodoo_home/static/tests/home.test.js`
- Modify: `monodoo_home/__manifest__.py`
- Modify: `tests/test_repository_contract.py`

**Interfaces:**
- Action registry tag: `monodoo_home`.
- XML IDs: `monodoo_home.action_monodoo_home`, `monodoo_home.menu_monodoo_home`.
- Shared constant: `MONODOO_HOME_MENU_XMLID`.
- App source: `menuService.getApps()`.
- App navigation: `menuService.selectMenu(app)`.

- [ ] **Step 1: Extend the repository contract first and verify RED**

Add tests that require:

```python
import xml.etree.ElementTree as ET


def test_home_manifest_declares_action_and_home_assets(self):
    manifest = load_manifest("monodoo_home")
    self.assertEqual(manifest["data"], ["data/home_action.xml"])
    self.assertEqual(
        manifest["assets"]["web.assets_backend"],
        ["monodoo_home/static/src/home/**/*"],
    )
    self.assertEqual(
        manifest["assets"]["web.assets_unit_tests"],
        ["monodoo_home/static/tests/**/*.test.js"],
    )


def test_home_xml_exists_and_parses(self):
    path = ROOT / "monodoo_home/data/home_action.xml"
    ET.parse(path)
    content = path.read_text(encoding="utf-8")
    self.assertIn('id="action_monodoo_home"', content)
    self.assertIn('id="menu_monodoo_home"', content)
```

Run:

```bash
python3 -m unittest tests.test_repository_contract -v
```

Expected: FAIL because Task 2 files/declarations do not exist.

- [ ] **Step 2: Create the standard client action and root menu**

`monodoo_home/data/home_action.xml`:

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

No parent menu. No navbar view inheritance.

- [ ] **Step 3: Add deterministic shared constant and failing HOOT tests**

`monodoo_home/static/src/home/constants.js`:

```javascript
export const MONODOO_HOME_MENU_XMLID = "monodoo_home.menu_monodoo_home";
```

Create `monodoo_home/static/tests/home.test.js` using Odoo 19 `defineMenus`, `defineActions`, `mountWithCleanup`, `contains`, `getService`, `useTestClientAction`, and `queryAllTexts`.

The core assertions are:

```javascript
import { expect, test } from "@odoo/hoot";
import { queryAllTexts } from "@odoo/hoot-dom";
import { animationFrame } from "@odoo/hoot-mock";
import {
    contains,
    defineActions,
    defineMenus,
    getService,
    mountWithCleanup,
    useTestClientAction,
} from "@web/../tests/web_test_helpers";

import { MonodooHome } from "@monodoo_home/home/home";

const testAction = useTestClientAction();
defineActions([
    { ...testAction, id: 1000, params: { description: "Home" } },
    { ...testAction, id: 1001, params: { description: "CRM" } },
    { ...testAction, id: 1002, params: { description: "Project" } },
]);
defineMenus([
    { id: 10, name: "Home", actionID: 1000, xmlid: "monodoo_home.menu_monodoo_home" },
    {
        id: 20,
        name: "CRM",
        actionID: 1001,
        xmlid: "crm.crm_menu_root",
        webIconData: "data:image/png;base64,AA==",
    },
    {
        id: 30,
        name: "Project",
        actionID: 1002,
        xmlid: "project.menu_main_pm",
        webIconData: undefined,
    },
]);

test("renders Odoo apps in order and excludes Home", async () => {
    await mountWithCleanup(MonodooHome);
    expect(".o_monodoo_app_card").toHaveCount(2);
    expect(queryAllTexts(".o_monodoo_app_name")).toEqual(["CRM", "Project"]);
    expect(".o_monodoo_home .o_app_icon").toHaveCount(1);
    expect(".o_monodoo_app_fallback_icon").toHaveCount(1);
});

test("filters locally by app name", async () => {
    await mountWithCleanup(MonodooHome);
    await contains(".o_monodoo_search").edit("pro", { confirm: false });
    await animationFrame();
    expect(queryAllTexts(".o_monodoo_app_name")).toEqual(["Project"]);
});

test("opens app through menu service", async () => {
    await mountWithCleanup(MonodooHome);
    await contains(".o_monodoo_app_card").click();
    await animationFrame();
    expect(getService("menu").getCurrentApp().name).toBe("CRM");
});
```

Also test:
- only Home returned -> `.o_monodoo_empty` exists;
- no app icon -> neutral fallback icon;
- search does not call `rpc`/fetch after mount.

At this point the test file may not execute until the runtime exists, but the production component is still implemented only after the test behavior is written.

- [ ] **Step 4: Implement the Owl component**

`home.js`:

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

`home.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="monodoo_home.Home">
        <div class="o_monodoo_home h-100 overflow-auto bg-view">
            <div class="container py-4 py-lg-5">
                <div class="mx-auto o_monodoo_home_inner">
                    <h1 class="h3 mb-4">Applications</h1>
                    <input
                        class="o_monodoo_search form-control mb-4"
                        type="search"
                        placeholder="Search applications..."
                        aria-label="Search applications"
                        t-model="state.query"
                    />
                    <div t-if="apps.length" class="row g-3">
                        <t t-foreach="apps" t-as="app" t-key="app.id">
                            <div class="col-6 col-sm-4 col-md-3 col-lg-2">
                                <button
                                    type="button"
                                    class="o_monodoo_app_card btn btn-light border w-100 h-100 p-3 d-flex flex-column align-items-center justify-content-center gap-2"
                                    t-on-click="() => this.openApp(app)"
                                >
                                    <img
                                        t-if="app.webIconData"
                                        class="o_app_icon"
                                        t-att-src="app.webIconData"
                                        t-att-alt="app.name"
                                    />
                                    <i
                                        t-else=""
                                        class="o_monodoo_app_fallback_icon oi oi-apps fs-2"
                                        aria-hidden="true"
                                    />
                                    <span class="o_monodoo_app_name text-truncate w-100" t-esc="app.name"/>
                                </button>
                            </div>
                        </t>
                    </div>
                    <div t-else="" class="o_monodoo_empty text-muted text-center py-5">
                        No applications available.
                    </div>
                </div>
            </div>
        </div>
    </t>
</templates>
```

`home.scss`:

```scss
.o_monodoo_home_inner {
    max-width: 1100px;
}

.o_monodoo_app_card {
    min-height: 7rem;

    .o_app_icon {
        width: 3rem;
        height: 3rem;
        object-fit: contain;
    }
}
```

Do not define a Monodoo color palette.

- [ ] **Step 5: Update the manifest only with files that now exist**

Add:

```python
"data": ["data/home_action.xml"],
"assets": {
    "web.assets_backend": ["monodoo_home/static/src/home/**/*"],
    "web.assets_unit_tests": ["monodoo_home/static/tests/**/*.test.js"],
},
```

- [ ] **Step 6: Run repository contract tests**

```bash
python3 -m unittest tests.test_repository_contract -v
```

Expected: PASS.

- [ ] **Step 7: Commit Task 2**

```bash
git add monodoo_home tests/test_repository_contract.py
git commit -m "feat: add Community application launcher"
```

---

### Task 3: Make neutral `/odoo` select Home with fail-open fallback

**Files:**
- Create: `monodoo_home/static/src/webclient/default_home.js`
- Create: `monodoo_home/static/tests/default_home.test.js`
- Modify: `monodoo_home/__manifest__.py`
- Modify: `tests/test_repository_contract.py`

**Interfaces:** Consumes `MONODOO_HOME_MENU_XMLID`, `WebClient.prototype._loadDefaultApp()`, `menuService.getApps()`, and `menuService.selectMenu()`.

- [ ] **Step 1: Write failing helper tests**

`default_home.test.js`:

```javascript
import { expect, test } from "@odoo/hoot";

import { MONODOO_HOME_MENU_XMLID } from "@monodoo_home/home/constants";
import { loadMonodooDefaultApp } from "@monodoo_home/webclient/default_home";

test("selects Monodoo Home when available", async () => {
    const home = { id: 10, xmlid: MONODOO_HOME_MENU_XMLID };
    let selected;
    let fallbackCalled = false;
    await loadMonodooDefaultApp(
        {
            getApps: () => [home, { id: 20, xmlid: "crm.crm_menu_root" }],
            selectMenu: async (menu) => { selected = menu; },
        },
        async () => { fallbackCalled = true; }
    );
    expect(selected).toBe(home);
    expect(fallbackCalled).toBe(false);
});

test("uses Odoo fallback when Home is missing", async () => {
    let fallbackCalled = false;
    await loadMonodooDefaultApp(
        { getApps: () => [{ id: 20, xmlid: "crm.crm_menu_root" }], selectMenu: async () => {} },
        async () => { fallbackCalled = true; }
    );
    expect(fallbackCalled).toBe(true);
});

test("uses Odoo fallback when Home selection fails", async () => {
    const home = { id: 10, xmlid: MONODOO_HOME_MENU_XMLID };
    let fallbackCalled = false;
    await loadMonodooDefaultApp(
        {
            getApps: () => [home],
            selectMenu: async () => { throw new Error("selection failed"); },
        },
        async () => { fallbackCalled = true; }
    );
    expect(fallbackCalled).toBe(true);
});
```

Add an Odoo `WebClient` test with `defineMenus()` + `mountWithCleanup(WebClient)` showing that no-state startup renders `.o_monodoo_home` instead of the first business app.

- [ ] **Step 2: Implement one isolated WebClient patch**

`default_home.js`:

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
        return loadMonodooDefaultApp(
            this.menuService,
            () => super._loadDefaultApp()
        );
    },
});
```

Do not patch `loadRouterState()`. That is what preserves valid deep links and restored state.

- [ ] **Step 3: Add the patch file to backend assets**

Final backend asset list becomes:

```python
"web.assets_backend": [
    "monodoo_home/static/src/home/**/*",
    "monodoo_home/static/src/webclient/default_home.js",
],
```

- [ ] **Step 4: Strengthen static contract checks**

Add tests that assert exactly one `patch(WebClient.prototype` occurrence under `monodoo_home`, no `patch(NavBar`, no `t-inherit="web.NavBar"`, and no `controllers/` directory.

- [ ] **Step 5: Run repository contract tests**

```bash
python3 -m unittest tests.test_repository_contract -v
```

Expected: PASS.

- [ ] **Step 6: Commit Task 3**

```bash
git add monodoo_home tests/test_repository_contract.py
git commit -m "feat: open Monodoo Home on neutral backend entry"
```

---

### Task 4: Add a real Odoo 19 runtime, HOOT gate, and browser acceptance suite

**Files:**
- Create: `tests/requirements.txt`
- Create: `tests/runtime/docker-compose.yml`
- Create: `tests/runtime/prepare_database.sh`
- Create: `tests/runtime/wait_http.py`
- Create: `tests/e2e/conftest.py`
- Create: `tests/e2e/test_home.py`
- Create: `tests/e2e/test_hoot.py`

**Interfaces:** Uses official `odoo:19.0`, `postgres:16`, `crm`, and `project` only as test fixtures around the two Monodoo addons.

- [ ] **Step 1: Pin browser-test dependencies**

`tests/requirements.txt`:

```text
playwright==1.55.0
pytest==8.4.2
```

If the package index used by CI cannot resolve one of these exact versions, update this file to the nearest available patch release in the same major/minor before committing; never leave an unpinned range.

- [ ] **Step 2: Create Docker Compose**

`tests/runtime/docker-compose.yml`:

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
    ports:
      - "8069:8069"
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

- [ ] **Step 3: Create deterministic HTTP wait helper**

`tests/runtime/wait_http.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

from urllib.error import HTTPError, URLError
from urllib.request import urlopen
import sys
import time

url = sys.argv[1]
timeout = float(sys.argv[2])
deadline = time.monotonic() + timeout
last_error: Exception | None = None

while time.monotonic() < deadline:
    try:
        with urlopen(url, timeout=3) as response:
            if response.status < 500:
                raise SystemExit(0)
    except (HTTPError, URLError, TimeoutError) as error:
        last_error = error
    time.sleep(1)

print(f"Timed out waiting for {url}: {last_error}", file=sys.stderr)
raise SystemExit(1)
```

- [ ] **Step 4: Create deterministic database preparation script**

`tests/runtime/prepare_database.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

docker compose down -v --remove-orphans
docker compose up -d db

# Fresh install proves addon data/assets can be registered on a clean Odoo 19 DB.
docker compose run --rm odoo \
  --database=monodoo_test \
  --stop-after-init \
  --without-demo=all \
  -i monodoo_core,monodoo_home,crm,project

# Deterministic credentials and a restricted internal test user.
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
    "groups_id": [(6, 0, [internal_group.id, project_group.id])],
}
if user:
    user.write(vals)
else:
    env["res.users"].create(vals)
env.cr.commit()
PY

# Upgrade must also succeed before browser tests are allowed to run.
docker compose run --rm odoo \
  --database=monodoo_test \
  --stop-after-init \
  --without-demo=all \
  -u monodoo_core,monodoo_home

docker compose up -d odoo
python3 wait_http.py http://127.0.0.1:8069/web/login 90
```

If Odoo 19's exact user-group write API differs in the official runtime, diagnose the real field/API and update this script to the Odoo 19-supported equivalent; do not broaden the user's groups merely to make the test pass.

- [ ] **Step 5: Create shared Playwright fixtures**

`tests/e2e/conftest.py`:

```python
from __future__ import annotations

import pytest
from playwright.sync_api import Browser, Page, sync_playwright

BASE_URL = "http://127.0.0.1:8069"


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def page(browser: Browser):
    context = browser.new_context()
    page = context.new_page()
    page_errors: list[str] = []
    page.on("pageerror", lambda error: page_errors.append(str(error)))
    yield page
    assert not page_errors, "Browser page errors: " + " | ".join(page_errors)
    context.close()


def login(page: Page, login_name: str, password: str) -> None:
    page.goto(f"{BASE_URL}/web/login")
    page.locator("input[name='login']").fill(login_name)
    page.locator("input[name='password']").fill(password)
    page.locator("button[type='submit']").click()
    page.wait_for_load_state("networkidle")
```

- [ ] **Step 6: Write browser acceptance tests**

`tests/e2e/test_home.py` covers five concrete flows:

```python
from playwright.sync_api import expect

from .conftest import BASE_URL, login


def test_neutral_odoo_opens_home_and_deep_link_survives(page):
    login(page, "admin", "admin")
    page.goto(f"{BASE_URL}/odoo")
    expect(page.locator(".o_monodoo_home")).to_be_visible()
    assert page.locator(".o_monodoo_app_card").count() > 1

    page.locator(".o_monodoo_app_card", has_text="CRM").click()
    expect(page.locator(".o_monodoo_home")).to_have_count(0)
    deep_link = page.url
    assert "/odoo" in deep_link

    page.goto(deep_link)
    page.wait_for_load_state("networkidle")
    expect(page.locator(".o_monodoo_home")).to_have_count(0)


def test_search_is_local(page):
    login(page, "admin", "admin")
    page.goto(f"{BASE_URL}/odoo")
    page.wait_for_load_state("networkidle")
    network_calls: list[str] = []
    page.on(
        "request",
        lambda request: network_calls.append(request.url)
        if request.resource_type in {"xhr", "fetch"}
        else None,
    )
    before = len(network_calls)
    page.locator(".o_monodoo_search").fill("Project")
    page.wait_for_timeout(250)
    assert len(network_calls) == before
    assert page.locator(".o_monodoo_app_card").count() == 1
    expect(page.locator(".o_monodoo_app_card")).to_contain_text("Project")


def test_standard_desktop_apps_menu_contains_home_and_returns_to_home(page):
    login(page, "admin", "admin")
    page.goto(f"{BASE_URL}/odoo")
    page.locator(".o_monodoo_app_card", has_text="CRM").click()
    page.locator(".o_navbar_apps_menu button[title='Home Menu']").click()
    expect(page.locator(".o_navbar_apps_menu .o_app", has_text="Home")).to_be_visible()
    page.locator(".o_navbar_apps_menu .o_app", has_text="Home").click()
    expect(page.locator(".o_monodoo_home")).to_be_visible()


def test_restricted_internal_user_sees_project_not_crm(page):
    login(page, "project.user@example.test", "project")
    page.goto(f"{BASE_URL}/odoo")
    expect(page.locator(".o_monodoo_app_card", has_text="Project")).to_be_visible()
    expect(page.locator(".o_monodoo_app_card", has_text="CRM")).to_have_count(0)


def test_mobile_standard_apps_navigation_exposes_home(page):
    page.set_viewport_size({"width": 390, "height": 844})
    login(page, "admin", "admin")
    page.goto(f"{BASE_URL}/odoo")
    page.locator(".o_monodoo_app_card", has_text="CRM").click()
    page.locator("a.o_menu_toggle").click()
    page.locator(".o_sidebar_topbar a.btn-primary").click()
    expect(page.locator(".o_app_menu_sidebar li.o_app", has_text="Home")).to_be_visible()
    page.locator(".o_app_menu_sidebar li.o_app", has_text="Home").click()
    expect(page.locator(".o_monodoo_home")).to_be_visible()
```

If a selector differs in the exact Odoo 19 runtime, update only the selector to the verified standard DOM. Do not alter the behavioral assertion.

- [ ] **Step 7: Add a HOOT execution gate using Odoo's own test page**

Odoo 19's `web` controller serves `/web/tests`, and its own `WebSuite.test_unit_desktop` runs `/web/tests?headless&loglevel=2&preset=desktop&timeout=15000` and waits for the console success signal `[HOOT] Test suite succeeded`.

Create `tests/e2e/test_hoot.py`:

```python
from .conftest import BASE_URL, login


def test_hoot_suite_succeeds(page):
    login(page, "admin", "admin")
    messages: list[str] = []
    page.on("console", lambda message: messages.append(message.text))
    page.goto(
        f"{BASE_URL}/web/tests?headless&loglevel=2&preset=desktop&timeout=15000",
        wait_until="domcontentloaded",
    )
    page.wait_for_function(
        """() => [...document.querySelectorAll('*')]
            .some((node) => node.textContent?.includes('[HOOT] Test suite succeeded'))""",
        timeout=3600000,
    )
    assert not any("[HOOT]" in message and "failed" in message.lower() for message in messages)
```

Before accepting this test implementation, inspect the exact Odoo 19 test page once. If the success signal exists only in console and not DOM, replace the `wait_for_function` with a Playwright `expect_console_message`/event-backed wait for the exact `[HOOT] Test suite succeeded` signal. The success criterion itself is fixed and comes from Odoo 19's own `WebSuite`.

- [ ] **Step 8: Run the full local runtime**

```bash
python3 -m venv .venv-test
. .venv-test/bin/activate
pip install -r tests/requirements.txt
python -m playwright install chromium
cd tests/runtime
chmod +x prepare_database.sh wait_http.py
./prepare_database.sh
cd ../..
pytest tests/e2e -q
```

Expected: fresh install succeeds, upgrade succeeds, HOOT succeeds, all browser acceptance tests pass, and no uncaught browser errors occur.

- [ ] **Step 9: Tear down and commit Task 4**

```bash
cd tests/runtime
docker compose down -v --remove-orphans
cd ../..
git add tests
git commit -m "test: add Odoo 19 runtime acceptance harness"
```

---

### Task 5: Add GitHub Actions release gates

**Files:**
- Create: `.github/workflows/ci.yml`
- Modify: `README.md`

- [ ] **Step 1: Create separate contract and runtime jobs**

`.github/workflows/ci.yml`:

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
        with:
          python-version: "3.12"
      - run: python -m unittest tests.test_repository_contract -v

  odoo-runtime:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
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

Do not remove the HOOT browser gate from `pytest tests/e2e`; it is part of runtime acceptance.

- [ ] **Step 2: Update README with exact local verification commands**

Document:

```bash
python3 -m unittest tests.test_repository_contract -v
python3 -m venv .venv-test
. .venv-test/bin/activate
pip install -r tests/requirements.txt
python -m playwright install chromium
tests/runtime/prepare_database.sh
pytest tests/e2e -q
```

Also document `http://localhost:8069/odoo`, module install names, and Odoo 19 Community-only support.

- [ ] **Step 3: Run the same commands locally before pushing**

Expected: all pass.

- [ ] **Step 4: Commit Task 5**

```bash
git add .github/workflows/ci.yml README.md
git commit -m "ci: validate Monodoo Home on Odoo 19"
```

- [ ] **Step 5: Push and inspect the workflow run**

```bash
git push -u origin feat/community-home
```

Record the GitHub Actions run ID and inspect every job conclusion. Do not call the branch green while any job is queued, running, skipped unexpectedly, or failed.

---

### Task 6: Release verification and PR

**Files:**
- Modify only if actual behavior requires reconciliation: `README.md`
- Modify only if actual implementation invalidates wording: `docs/superpowers/specs/2026-09-05-monodoo-home-design.md`

- [ ] **Step 1: Re-run the complete clean verification sequence**

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

Expected: PASS for contract, install, upgrade, HOOT, desktop browser, mobile browser, and restricted-user behavior.

- [ ] **Step 2: Map every acceptance criterion to evidence**

Verify all 19 criteria from spec section 9. Static inspection must additionally prove:

```bash
grep -R "facodi" monodoo_core monodoo_home && exit 1 || true
grep -R "patch(NavBar\|t-inherit=\"web.NavBar\"" monodoo_home && exit 1 || true
test ! -d monodoo_home/controllers
test ! -d monodoo_core/controllers
```

The only WebClient prototype patch should be the one in `default_home.js`.

- [ ] **Step 3: Re-check the exact upstream Odoo 19 integration contracts**

Before opening the PR, compare the current Odoo 19 source used by CI and confirm:

- `WebClient.loadRouterState()` calls `_loadDefaultApp()` only when no state is loaded.
- `_loadDefaultApp()` selects the first root app.
- `menuService.getApps()` returns root children.
- `menuService.selectMenu()` uses the standard action service and current-menu synchronization.
- desktop/mobile app navigation consumes the standard root-app list.

If any contract changed, stop and update code/tests/spec instead of forcing the old integration.

- [ ] **Step 4: Reconcile docs only with behavior actually proven**

Do not add favorites, dashboards, branding, profiles, auto-install engines, or multi-version promises to v1 documentation.

- [ ] **Step 5: Open the implementation PR**

PR title:

```text
Add Odoo 19 Community Home launcher
```

PR body summarizes:

- `monodoo_core` + `monodoo_home` boundaries;
- standard root-menu/client-action design;
- isolated `_loadDefaultApp()` fallback patch;
- permission inheritance through Odoo menu service;
- contract/HOOT/runtime/browser evidence with run IDs;
- explicit statement that `facodi-deploy` is not modified.

- [ ] **Step 6: Merge only after green PR CI**

Fetch the PR workflow run and inspect every job. Merge only when all required jobs conclude `success`.

- [ ] **Step 7: Verify post-merge `main`**

Fetch the resulting `main` SHA and its workflow run. Only call Monodoo v1 independently green when post-merge CI also concludes `success`.

---

## Separate Follow-up Gate: `facodi-deploy`

Do **not** implement FACODI deployment integration under this plan. Once Task 6 produces a merged Monodoo `main` SHA with green post-merge CI, write a separate `facodi-deploy` plan using that exact SHA. The follow-up must add `addons/monodoo` as a pinned git submodule, add `monodoo_core,monodoo_home` to `FACODI_MODULES`, verify the current nested-addon Docker discovery, extend authenticated `/odoo` runtime acceptance, verify existing Website/eLearning/deep-link behavior, and merge only after the canonical Coolify/runtime acceptance is green.
