import { Component, onWillStart, useState } from "@odoo/owl";
import { user } from "@web/core/user";
import { useBus, useService } from "@web/core/utils/hooks";

const SIDEBAR_MODES = new Set(["auto", "expanded", "compact", "hidden"]);

export class MonodooAppsBar extends Component {
    static template = "monodoo_appsbar.AppsBar";
    static props = ["*"];

    setup() {
        this.menuService = useService("menu");
        this.orm = useService("orm");
        this.state = useState({
            mode: "auto",
            menuRevision: 0,
        });

        useBus(this.env.bus, "MENUS:APP-CHANGED", () => {
            this.state.menuRevision += 1;
        });

        onWillStart(async () => {
            try {
                const [record] = await this.orm.read(
                    "res.users",
                    [user.userId],
                    ["monodoo_sidebar_mode"]
                );
                const mode = record?.monodoo_sidebar_mode;
                this.state.mode = SIDEBAR_MODES.has(mode) ? mode : "auto";
            } catch {
                this.state.mode = "auto";
            }
        });
    }

    get apps() {
        void this.state.menuRevision;
        return this.menuService.getApps();
    }

    get currentApp() {
        void this.state.menuRevision;
        return this.menuService.getCurrentApp();
    }

    isActive(app) {
        return this.currentApp?.id === app.id;
    }

    openApp(app) {
        return this.menuService.selectMenu(app);
    }
}
