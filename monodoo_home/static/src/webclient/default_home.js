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
