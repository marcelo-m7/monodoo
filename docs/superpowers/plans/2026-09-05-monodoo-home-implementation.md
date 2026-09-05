# Monodoo Home Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `monodoo_core` and `monodoo_home` for Odoo 19 Community so neutral `/odoo` opens a native application launcher while valid deep links, Odoo permissions, standard navigation, and fail-open behavior remain intact.

**Architecture:** `monodoo_core` is a deliberately minimal generic base addon. `monodoo_home` registers a standard root `ir.ui.menu` bound to an Owl `ir.actions.client`, reads permitted applications from the existing Odoo menu service, and applies one isolated patch to `WebClient._loadDefaultApp()` so only the no-state fallback selects Home. The launcher never queries `ir.ui.menu` independently and never replaces `/odoo`, authentication, the navbar, or Odoo's ACL model.

**Tech Stack:** Odoo 19 Community, Python manifests/XML data, Owl, Odoo web registries/services, HOOT frontend tests, Docker/PostgreSQL runtime validation, Playwright browser acceptance tests, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-05-monodoo-home-design.md`

## Global Constraints

- Target runtime is Odoo 19 Community only.
- Initial versions are exactly `19.0.1.0.0` for both `monodoo_core` and `monodoo_home`.
- License is LGPL-3.
- `monodoo_home` depends on `web` and `monodoo_core`; `monodoo_core` depends only on `base` in v1.
- No FACODI dependency, naming, data model, URL, or behavior may appear in either addon.
- Do not add compatibility abstractions for Odoo 17, 18, or 20.
- Do not create a custom `/odoo` controller or redirect.
- Do not patch or replace the standard navbar template.
- Home must be a standard root `ir.ui.menu` available to `base.group_user` and bound to a standard `ir.actions.client`.
- Business application cards come only from `menuService.getApps()` and must preserve Odoo order after filtering out Home itself.
- Opening a card uses `menuService.selectMenu(app)`.
- Search is local-only and must not trigger an RPC.
- The default-home adapter must fail open to the original Odoo `_loadDefaultApp()` behavior.
- A green install without browser/frontend verification is insufficient for release.
- `facodi-deploy` integration is a separate follow-up plan and must not begin until Monodoo is merged and independently green.

---

## File Structure

Create the following implementation shape. Each file has one responsibility.

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
│       └── test_home.py
├── monodoo_core/
│   ├── __init__.py
│   └── __manifest__.py
└── monodoo_home/
    ├── __init__.py
    ├── __manifest__.py
    ├── data/
    │   └── home_action.xml
    ├── static/
    │   ├── src/
    │   │   ├── home/
    │   │   │   ├── home.js
    │   │   │   ├── home.xml
    │   │   │   └── home.scss
    │   │   └── webclient/
    │   │       └── default_home.js
    │   └── tests/
    │       ├── home.test.js
    │       └── default_home.test.js
```

No Python model package is created in v1 because neither addon needs a custom business model.

---

### Task 1: Establish the repository contract and minimal Odoo addons

**Files:**
- Create: `LICENSE`
- Create: `README.md`
- Create: `tests/__init__.py`
- Create: `tests/test_repository_contract.py`
- Create: `monodoo_core/__init__.py`
- Create: `monodoo_core/__manifest__.py`
- Create: `monodoo_home/__init__.py`
- Create: `monodoo_home/__manifest__.py`

**Interfaces:**
- Consumes: approved design in `docs/superpowers/specs/2026-09-05-monodoo-home-design.md`.
- Produces: installable addon manifests with module names `monodoo_core` and `monodoo_home`; the latter declares backend and unit-test asset bundles used by later tasks.

- [ ] **Step 1: Write the failing repository contract test**

Create `tests/test_repository_contract.py` with checks that parse manifests through `ast.literal_eval`, assert exact versions/license/dependencies, reject FACODI references in addon source, reject controller files, and ensure every declared local asset path exists.

```python
from __future__ import annotations

import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
ADDONS = ("monodoo_core", "monodoo_home")


def load_manifest(addon: str) -> dict:
    path = ROOT / addon / "__manifest__.py"
    return ast.literal_eval(path.read_text(encoding="utf-8"))


class RepositoryContractTest(unittest.TestCase):
    def test_expected_addons_exist(self):
        for addon in ADDONS:
            self.assertTrue((ROOT / addon / "__manifest__.py").is_file())
            self.assertTrue((ROOT / addon / "__init__.py").is_file())

    def test_versions_and_license(self):
        for addon in ADDONS:
            manifest = load_manifest(addon)
            self.assertEqual(manifest["version"], "19.0.1.0.0")
            self.assertEqual(manifest["license"], "LGPL-3")
            self.assertTrue(manifest["installable"])

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
                    self.assertNotIn("facodi", path.read_text(encoding="utf-8").lower())

    def test_no_http_controller(self):
        for addon in ADDONS:
            self.assertFalse((ROOT / addon / "controllers").exists())

    def test_home_assets_are_declared(self):
        manifest = load_manifest("monodoo_home")
        assets = manifest["assets"]
        self.assertIn("web.assets_backend", assets)
        self.assertIn("web.assets_unit_tests", assets)
        backend = assets["web.assets_backend"]
        self.assertIn("monodoo_home/static/src/home/**/*", backend)
        self.assertIn(
            "monodoo_home/static/src/webclient/default_home.js",
            backend,
        )
        self.assertEqual(
            assets["web.assets_unit_tests"],
            ["monodoo_home/static/tests/**/*.test.js"],
        )


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the contract test and verify it fails**

Run:

```bash
python3 -m unittest tests.test_repository_contract -v
```

Expected: FAIL because `monodoo_core` and `monodoo_home` do not yet exist.

- [ ] **Step 3: Add the minimal addon manifests and LGPL-3 repository metadata**

Create `monodoo_core/__manifest__.py`:

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

Create `monodoo_home/__manifest__.py` initially with the final dependency and asset contract; the referenced files are added in Tasks 2 and 3, so the contract's file-existence expansion is added only when those tasks land.

```python
{
    "name": "Monodoo Home",
    "summary": "Native Community application launcher for Odoo 19",
    "version": "19.0.1.0.0",
    "category": "Productivity",
    "license": "LGPL-3",
    "depends": ["web", "monodoo_core"],
    "data": ["data/home_action.xml"],
    "assets": {
        "web.assets_backend": [
            "monodoo_home/static/src/home/**/*",
            "monodoo_home/static/src/webclient/default_home.js",
        ],
        "web.assets_unit_tests": [
            "monodoo_home/static/tests/**/*.test.js",
        ],
    },
    "installable": True,
    "application": False,
}
```

Both `__init__.py` files remain empty except for a short module docstring; do not create unused model imports.

`README.md` must state: Odoo 19 Community, LGPL-3, current modules, install order, and that FACODI integration lives outside this repository.

- [ ] **Step 4: Adjust the contract test so Task 1 validates only files Task 1 owns**

Do not weaken dependency/version checks. Delay only XML/asset path existence checks until Tasks 2 and 3; keep the asset bundle declaration assertions above.

- [ ] **Step 5: Run the repository contract test**

Run:

```bash
python3 -m unittest tests.test_repository_contract -v
```

Expected: PASS.

- [ ] **Step 6: Commit Task 1**

```bash
git add LICENSE README.md tests monodoo_core monodoo_home
 git commit -m "feat: establish Monodoo addon foundation"
```

---

### Task 2: Implement the standard Home client action and application launcher

**Files:**
- Create: `monodoo_home/data/home_action.xml`
- Create: `monodoo_home/static/src/home/home.js`
- Create: `monodoo_home/static/src/home/home.xml`
- Create: `monodoo_home/static/src/home/home.scss`
- Create: `monodoo_home/static/tests/home.test.js`
- Modify: `tests/test_repository_contract.py`

**Interfaces:**
- Consumes: Odoo `menu` service methods `getApps()` and `selectMenu(menu)`.
- Produces: action registry tag `monodoo_home`; XML IDs `monodoo_home.action_monodoo_home` and `monodoo_home.menu_monodoo_home`; constant `MONODOO_HOME_MENU_XMLID = "monodoo_home.menu_monodoo_home"`; Owl class `MonodooHome`.

- [ ] **Step 1: Write the failing HOOT tests for launcher behavior**

Create `monodoo_home/static/tests/home.test.js` using Odoo 19's own `defineMenus`, `defineActions`, `mountWithCleanup`, `contains`, `getService`, and `useTestClientAction` helpers. The first tests must prove:

```javascript
import { expect, test } from "@odoo/hoot";
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
    {
        id: 10,
        name: "Home",
        actionID: 1000,
        xmlid: "monodoo_home.menu_monodoo_home",
    },
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

test("renders permitted apps in Odoo order and excludes Home", async () => {
    await mountWithCleanup(MonodooHome);
    expect(".o_monodoo_app_card").toHaveCount(2);
    expect(".o_monodoo_app_name").toHaveText("CRM\nProject");
    expect(".o_monodoo_home .o_app_icon").toHaveCount(1);
    expect(".o_monodoo_app_fallback_icon").toHaveCount(1);
});

test("filters locally by application name", async () => {
    await mountWithCleanup(MonodooHome);
    await contains(".o_monodoo_search").edit("pro", { confirm: false });
    await animationFrame();
    expect(".o_monodoo_app_card").toHaveCount(1);
    expect(".o_monodoo_app_name").toHaveText("Project");
});

test("opens an app through the menu service", async () => {
    await mountWithCleanup(MonodooHome);
    await contains(".o_monodoo_app_card").click();
    await animationFrame();
    expect(getService("menu").getCurrentApp().name).toBe("CRM");
});
```

Add one test that patches `getApps()` to return only Home and asserts `.o_monodoo_empty` exists, and one test that instruments network calls around editing `.o_monodoo_search` and asserts no new call occurred after typing.

- [ ] **Step 2: Run only the Monodoo Home frontend tests and verify they fail**

Run Odoo's HOOT suite with the module filter once the runtime helper from Task 4 exists. During this task, a local Odoo checkout may be used directly:

```bash
./odoo-bin -d monodoo_test --addons-path=addons,/path/to/monodoo \
  --test-enable --stop-after-init -i monodoo_home
```

Then open/run the Odoo unit-test bundle filtered to `monodoo_home`. Expected: tests fail because the component/action do not exist yet.

- [ ] **Step 3: Create the standard `ir.actions.client` and root `ir.ui.menu`**

Create `monodoo_home/data/home_action.xml`:

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

Do not add a parent menu and do not add a custom navbar view.

- [ ] **Step 4: Implement the Owl component with no server-side menu query**

Create `monodoo_home/static/src/home/home.js`:

```javascript
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, useState } from "@odoo/owl";

export const MONODOO_HOME_MENU_XMLID = "monodoo_home.menu_monodoo_home";

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
        if (!query) {
            return apps;
        }
        return apps.filter((app) =>
            (app.name || "").toLocaleLowerCase().includes(query)
        );
    }

    openApp(app) {
        return this.menuService.selectMenu(app);
    }
}

registry.category("actions").add("monodoo_home", MonodooHome);
```

Create `home.xml` with exactly one search input, an ordered card grid, Odoo-provided image data where present, a neutral `oi oi-apps` fallback where absent, and a neutral empty state. Keep all visible strings translatable through the Owl/QWeb template.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="monodoo_home.Home">
        <div class="o_monodoo_home h-100 overflow-auto bg-view">
            <div class="container py-4 py-lg-5">
                <div class="mx-auto" style="max-width: 1100px;">
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

`home.scss` may size `.o_app_icon` to `3rem` and keep cards keyboard-visible, but must not define a Monodoo color palette or replace Odoo CSS variables.

- [ ] **Step 5: Strengthen the repository contract for the new files**

Add assertions that:

- `data/home_action.xml` parses.
- it contains `action_monodoo_home` and `menu_monodoo_home`.
- no XML file contains a route/controller declaration.
- every static path referenced by the manifest exists.

- [ ] **Step 6: Run contract + frontend tests**

Expected: all Task 1/2 tests pass.

- [ ] **Step 7: Commit Task 2**

```bash
git add monodoo_home/data monodoo_home/static/src/home monodoo_home/static/tests/home.test.js tests/test_repository_contract.py
 git commit -m "feat: add Community application launcher"
```

---

### Task 3: Implement automatic neutral `/odoo` Home with fail-open fallback

**Files:**
- Create: `monodoo_home/static/src/webclient/default_home.js`
- Create: `monodoo_home/static/tests/default_home.test.js`
- Modify: `tests/test_repository_contract.py`

**Interfaces:**
- Consumes: `MONODOO_HOME_MENU_XMLID`, Odoo 19 `WebClient.prototype._loadDefaultApp()`, and `menuService.getApps()/selectMenu()`.
- Produces: exported helper `loadMonodooDefaultApp(menuService, fallback)` and one isolated `patch(WebClient.prototype, {...})`.

- [ ] **Step 1: Write failing tests for Home selection and fallback behavior**

Create `default_home.test.js` and test the helper directly with stub services before testing it through `WebClient`.

```javascript
import { expect, test } from "@odoo/hoot";

import {
    loadMonodooDefaultApp,
    MONODOO_HOME_MENU_XMLID,
} from "@monodoo_home/webclient/default_home";

test("selects the Monodoo Home root menu", async () => {
    const home = { id: 10, xmlid: MONODOO_HOME_MENU_XMLID };
    let selected;
    let fallbackCalled = false;
    await loadMonodooDefaultApp(
        {
            getApps: () => [home, { id: 20, xmlid: "crm.crm_menu_root" }],
            selectMenu: async (menu) => {
                selected = menu;
            },
        },
        async () => {
            fallbackCalled = true;
        }
    );
    expect(selected).toBe(home);
    expect(fallbackCalled).toBe(false);
});

test("falls back when Home is missing", async () => {
    let fallbackCalled = false;
    await loadMonodooDefaultApp(
        {
            getApps: () => [{ id: 20, xmlid: "crm.crm_menu_root" }],
            selectMenu: async () => {},
        },
        async () => {
            fallbackCalled = true;
        }
    );
    expect(fallbackCalled).toBe(true);
});

test("falls back when selecting Home fails", async () => {
    const home = { id: 10, xmlid: MONODOO_HOME_MENU_XMLID };
    let fallbackCalled = false;
    await loadMonodooDefaultApp(
        {
            getApps: () => [home],
            selectMenu: async () => {
                throw new Error("selection failed");
            },
        },
        async () => {
            fallbackCalled = true;
        }
    );
    expect(fallbackCalled).toBe(true);
});
```

Add a WebClient-level test using `defineMenus()` and `mountWithCleanup(WebClient)` to prove that a no-state startup renders `.o_monodoo_home` rather than the first business app.

- [ ] **Step 2: Run the tests and verify they fail because the adapter does not exist**

Expected: module import failure for `@monodoo_home/webclient/default_home`.

- [ ] **Step 3: Implement the helper and the single WebClient patch**

Create `default_home.js`:

```javascript
import { patch } from "@web/core/utils/patch";
import { WebClient } from "@web/webclient/webclient";

export const MONODOO_HOME_MENU_XMLID = "monodoo_home.menu_monodoo_home";

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

Do not patch `loadRouterState()`: valid state/deep-link handling must remain entirely Odoo-owned. Do not catch errors outside the Home-selection attempt.

- [ ] **Step 4: Remove the duplicate XML-ID constant from `home.js`**

Import the shared constant from `default_home.js` or, preferably, extract the constant into `static/src/home/constants.js` only if doing so removes a real circular dependency. If `home.js -> default_home.js` causes the WebClient patch to load as a side effect when testing the component, create `static/src/home/constants.js` with only:

```javascript
export const MONODOO_HOME_MENU_XMLID = "monodoo_home.menu_monodoo_home";
```

Then import that constant from both files. This is the only additional file permitted for this concern.

- [ ] **Step 5: Add static contract checks for the patch boundary**

The repository contract must assert:

- there is exactly one `patch(WebClient.prototype` occurrence under `monodoo_home`;
- no source file contains `patch(NavBar` or `t-inherit="web.NavBar"`;
- no source file declares `/odoo` as a controller route.

- [ ] **Step 6: Run all repository and HOOT tests**

Expected: PASS, including fail-open tests.

- [ ] **Step 7: Commit Task 3**

```bash
git add monodoo_home/static/src monodoo_home/static/tests/default_home.test.js tests/test_repository_contract.py
 git commit -m "feat: open Monodoo Home on neutral backend entry"
```

---

### Task 4: Add a real Odoo 19 Community runtime harness and browser acceptance tests

**Files:**
- Create: `tests/requirements.txt`
- Create: `tests/runtime/docker-compose.yml`
- Create: `tests/runtime/prepare_database.sh`
- Create: `tests/runtime/wait_http.py`
- Create: `tests/e2e/test_home.py`

**Interfaces:**
- Consumes: official `odoo:19.0` image, PostgreSQL 16, installed `monodoo_core`, `monodoo_home`, `crm`, and `project` Community modules.
- Produces: repeatable local command that validates clean install, upgrade, browser startup, neutral Home, app navigation, deep-link preservation, restricted-user filtering, desktop apps menu, and mobile app navigation.

- [ ] **Step 1: Create the test Python dependency lock surface**

`tests/requirements.txt`:

```text
playwright==1.55.0
pytest==8.4.2
```

If either exact pin is unavailable in the execution environment, choose the newest patch release available for that same major/minor and commit the resolved pin; do not leave an unpinned dependency.

- [ ] **Step 2: Create Docker Compose for PostgreSQL and Odoo 19**

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

- [ ] **Step 3: Write a deterministic database preparation script**

`prepare_database.sh` must:

1. `docker compose down -v --remove-orphans`.
2. start `db` and wait healthy.
3. run one-shot Odoo init with `-i monodoo_core,monodoo_home,crm,project --stop-after-init`.
4. use Odoo shell to set the admin password to `admin`.
5. create an internal restricted user `project.user@example.test` with `base.group_user` and `project.group_project_user`, but without CRM sales groups.
6. run `-u monodoo_core,monodoo_home --stop-after-init` to prove upgrade safety.
7. start the persistent `odoo` service.
8. call `wait_http.py http://127.0.0.1:8069/web/login 90`.

Every command uses `set -euo pipefail`; failures stop the script.

- [ ] **Step 4: Write `wait_http.py`**

Use only Python stdlib (`urllib.request`, `time`, `sys`). It exits 0 only after an HTTP response below 500 and exits 1 after the supplied timeout, printing the last exception.

- [ ] **Step 5: Write Playwright tests first and verify they fail before running the server with the feature**

`tests/e2e/test_home.py` must provide a login helper and these tests:

```python
from playwright.sync_api import Page, expect

BASE_URL = "http://127.0.0.1:8069"


def login(page: Page, login: str, password: str) -> None:
    page.goto(f"{BASE_URL}/web/login")
    page.locator("input[name='login']").fill(login)
    page.locator("input[name='password']").fill(password)
    page.locator("button[type='submit']").click()
    page.wait_for_load_state("networkidle")


def test_neutral_odoo_opens_home_and_preserves_deep_link(page: Page):
    login(page, "admin", "admin")
    page.goto(f"{BASE_URL}/odoo")
    expect(page.locator(".o_monodoo_home")).to_be_visible()
    expect(page.locator(".o_monodoo_app_card")).to_have_count_greater_than(1)

    page.locator(".o_monodoo_app_card", has_text="CRM").click()
    expect(page.locator(".o_monodoo_home")).to_have_count(0)
    deep_link = page.url
    assert "/odoo" in deep_link

    page.goto(deep_link)
    page.wait_for_load_state("networkidle")
    expect(page.locator(".o_monodoo_home")).to_have_count(0)
```

Use normal Playwright count/assert patterns supported by the pinned version; if `to_have_count_greater_than` is unavailable, replace it with `assert locator.count() > 1` rather than weakening the assertion.

Additional tests must assert:

- Home is present in the standard desktop Apps dropdown.
- selecting Home from that dropdown returns to `.o_monodoo_home`.
- searching `Project` reduces the launcher to Project and produces no network request after the initial page load; collect requests before typing and assert the request count does not increase.
- `project.user@example.test` sees Project but does not see CRM.
- at mobile viewport `390x844`, the standard apps sidebar opens and contains Home; selecting it reaches `.o_monodoo_home`.

- [ ] **Step 6: Run the full local acceptance harness**

```bash
python3 -m venv .venv-test
. .venv-test/bin/activate
pip install -r tests/requirements.txt
python -m playwright install chromium
cd tests/runtime
./prepare_database.sh
cd ../..
pytest tests/e2e -q
```

Expected: all tests pass and no JS/Owl console error appears. Configure the Playwright context/test fixture to fail the test on uncaught `pageerror`; collect console errors and fail on errors originating from `monodoo_home`.

- [ ] **Step 7: Tear down the runtime and commit**

```bash
cd tests/runtime && docker compose down -v --remove-orphans && cd ../..
git add tests
 git commit -m "test: add Odoo 19 runtime acceptance harness"
```

---

### Task 5: Add GitHub Actions CI with contract, frontend, install/upgrade, and browser gates

**Files:**
- Create: `.github/workflows/ci.yml`
- Modify: `README.md`

**Interfaces:**
- Consumes: Tasks 1-4 test commands.
- Produces: required CI evidence for the Monodoo release; no deployment mutation.

- [ ] **Step 1: Create a CI workflow with separate readable jobs**

The workflow triggers on `push` and `pull_request` and contains at least:

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
      - run: tests/runtime/prepare_database.sh
      - run: pytest tests/e2e -q
      - if: always()
        run: cd tests/runtime && docker compose logs --no-color
      - if: always()
        run: cd tests/runtime && docker compose down -v --remove-orphans
```

If HOOT tests need a separate invocation not covered by the browser runtime, add a third `odoo-unit-tests` job rather than hiding them inside the E2E job. That job must run only `monodoo_home/static/tests/**/*.test.js` through Odoo 19's `web.assets_unit_tests` test runner and fail on any HOOT failure.

- [ ] **Step 2: Make CI run the clean-install and upgrade gates before browser tests**

Do not start browser acceptance against a database that skipped `-u monodoo_core,monodoo_home`. The runtime script remains the single source of truth for this sequence.

- [ ] **Step 3: Update README with exact local verification commands**

Document:

```bash
python3 -m unittest tests.test_repository_contract -v
cd tests/runtime && ./prepare_database.sh && cd ../..
pytest tests/e2e -q
```

Also document the URL `http://localhost:8069/odoo` for local inspection and state that the first release supports Odoo 19 Community only.

- [ ] **Step 4: Push the implementation branch and wait for CI**

Do not merge based on local success alone. Record the workflow run ID and inspect every job conclusion.

- [ ] **Step 5: Commit Task 5**

```bash
git add .github/workflows/ci.yml README.md
 git commit -m "ci: validate Monodoo Home on Odoo 19"
```

---

### Task 6: Release verification, documentation reconciliation, and PR

**Files:**
- Modify: `README.md`
- Modify only if needed for factual reconciliation: `docs/superpowers/specs/2026-09-05-monodoo-home-design.md`

**Interfaces:**
- Consumes: all prior implementation and CI evidence.
- Produces: reviewable PR for Monodoo v1; no `facodi-deploy` changes.

- [ ] **Step 1: Run the complete verification sequence from a clean workspace**

```bash
python3 -m unittest tests.test_repository_contract -v
python3 -m venv .venv-test
. .venv-test/bin/activate
pip install -r tests/requirements.txt
python -m playwright install chromium
cd tests/runtime
./prepare_database.sh
cd ../..
pytest tests/e2e -q
```

Then run the dedicated HOOT suite. All must pass before claiming the release is ready.

- [ ] **Step 2: Verify the 19 acceptance criteria explicitly**

Create a local review checklist mapping every criterion from spec section 9 to one automated test or direct inspection. In particular, manually inspect the repository for:

```bash
grep -R "route.*odoo\|/odoo" monodoo_core monodoo_home || true
grep -R "facodi" monodoo_core monodoo_home || true
grep -R "patch(NavBar\|web.NavBar" monodoo_home || true
```

Expected: no controller override, no FACODI coupling, no navbar patch. The literal `/odoo` may appear only in documentation/tests discussing expected routing, not in a custom controller implementation.

- [ ] **Step 3: Review the patch against the exact Odoo 19 source again**

Confirm before PR that upstream still has:

- `WebClient.loadRouterState()` calling `_loadDefaultApp()` only when no state loaded.
- `_loadDefaultApp()` selecting the first root app.
- menu service `getApps()` returning root children.
- `selectMenu()` using the standard action service and current-menu synchronization.
- standard desktop/mobile navbar reading `menuService.getApps()`.

If any of these exact contracts changed, stop and update the implementation/spec rather than forcing the old patch.

- [ ] **Step 4: Reconcile README/spec with actual implementation without inflating scope**

Documentation must describe only behavior proven by tests. Do not add favorites, dashboards, branding, configuration profiles, or multi-version promises.

- [ ] **Step 5: Open the implementation PR**

Use a branch such as `feat/community-home` created at execution time from the then-current `main`. PR title:

```text
Add Odoo 19 Community Home launcher
```

PR body must summarize:

- `monodoo_core` + `monodoo_home` boundaries;
- standard root-menu/client-action design;
- isolated `_loadDefaultApp()` fallback patch;
- permission inheritance through Odoo menu service;
- contract/HOOT/runtime/browser test evidence;
- explicit statement that `facodi-deploy` is not modified in this PR.

- [ ] **Step 6: Require green PR CI before merge**

Fetch the PR workflow run, inspect every job, and merge only when all required jobs conclude `success`. After merge, verify the workflow on the resulting `main` SHA before calling Monodoo v1 independently green.

- [ ] **Step 7: Commit any final documentation-only reconciliation if necessary**

```bash
git add README.md docs/superpowers/specs/2026-09-05-monodoo-home-design.md
 git commit -m "docs: reconcile Monodoo Home release behavior"
```

Skip this commit when no factual documentation change is needed.

---

## Follow-up Gate: `facodi-deploy`

Do **not** include deployment integration in this implementation plan. Once Task 6 has produced a merged Monodoo `main` SHA with green post-merge CI, create a separate plan for `marcelo-m7/facodi-deploy` that:

1. adds `addons/monodoo` as a git submodule pinned to the verified Monodoo SHA;
2. adds `monodoo_core,monodoo_home` to `FACODI_MODULES`;
3. confirms the existing Docker addon discovery copies both nested addons;
4. extends FACODI runtime acceptance so authenticated neutral `/odoo` renders `.o_monodoo_home`;
5. validates FACODI deep links and existing Website/eLearning flows are unchanged;
6. merges only after the canonical Coolify/runtime acceptance is green.

This second plan must use the exact merged Monodoo SHA as its input; it must not copy Monodoo source into `facodi-deploy`.
