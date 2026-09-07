#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

docker compose down -v --remove-orphans
docker compose up -d db

docker compose run --rm odoo \
  --database=monodoo_test --stop-after-init --without-demo=True \
  -i monodoo_core,monodoo_home,monodoo_theme,monodoo_appsbar,crm,project

cat <<'PY' | docker compose run --rm -T odoo odoo shell -d monodoo_test
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
  --database=monodoo_test --stop-after-init --without-demo=True \
  -u monodoo_core,monodoo_home,monodoo_theme,monodoo_appsbar

docker compose up -d odoo
python3 wait_http.py http://127.0.0.1:8069/web/login 90
