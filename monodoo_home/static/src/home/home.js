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
