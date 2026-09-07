import { Component, onWillStart, useState } from "@odoo/owl";
import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";
import { user } from "@web/core/user";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";

import { MONODOO_HOME_MENU_XMLID } from "./constants";
import {
    getRecentStorageKey,
    normalizeRecentApps,
    readRecentApps,
    writeRecentApps,
} from "./navigation_state";

export class MonodooHome extends Component {
    static template = "monodoo_home.Home";
    static props = ["*"];

    setup() {
        this.menuService = useService("menu");
        this.orm = useService("orm");
        this.recentStorageKey = getRecentStorageKey(session.db, user.userId);
        this.favoriteSaveQueue = Promise.resolve();
        this.favoriteSaveGeneration = 0;
        this.state = useState({
            query: "",
            favoriteXmlids: [],
            recentXmlids: [],
        });

        onWillStart(async () => {
            this.state.recentXmlids = readRecentApps(
                browser.localStorage,
                this.recentStorageKey
            );
            try {
                const preferences = await this.orm.call(
                    "res.users",
                    "get_monodoo_navigation_preferences",
                    []
                );
                this.state.favoriteXmlids = Array.isArray(preferences?.favorite_app_xmlids)
                    ? preferences.favorite_app_xmlids
                    : [];
            } catch (error) {
                browser.console.warn(
                    "Monodoo Home could not load favorite applications",
                    error
                );
            }
        });
    }

    get businessApps() {
        return this.menuService
            .getApps()
            .filter((app) => app.xmlid !== MONODOO_HOME_MENU_XMLID);
    }

    matchesQuery(app) {
        const query = this.state.query.trim().toLocaleLowerCase();
        return !query || (app.name || "").toLocaleLowerCase().includes(query);
    }

    get apps() {
        return this.businessApps.filter((app) => this.matchesQuery(app));
    }

    get favoriteApps() {
        const favorites = new Set(this.state.favoriteXmlids);
        return this.apps.filter((app) => favorites.has(app.xmlid));
    }

    get recentApps() {
        const appsByXmlid = new Map(this.apps.map((app) => [app.xmlid, app]));
        return this.state.recentXmlids
            .map((xmlid) => appsByXmlid.get(xmlid))
            .filter(Boolean);
    }

    isFavorite(app) {
        return this.state.favoriteXmlids.includes(app.xmlid);
    }

    async toggleFavorite(app) {
        if (!app.xmlid) {
            return;
        }
        const previous = [...this.state.favoriteXmlids];
        const next = this.isFavorite(app)
            ? previous.filter((xmlid) => xmlid !== app.xmlid)
            : [...previous, app.xmlid];
        const generation = ++this.favoriteSaveGeneration;
        this.state.favoriteXmlids = next;

        const save = async () => {
            try {
                const saved = await this.orm.call(
                    "res.users",
                    "set_monodoo_favorite_apps",
                    [next]
                );
                if (
                    generation === this.favoriteSaveGeneration &&
                    Array.isArray(saved)
                ) {
                    this.state.favoriteXmlids = saved;
                }
            } catch (error) {
                if (generation === this.favoriteSaveGeneration) {
                    this.state.favoriteXmlids = previous;
                }
                browser.console.warn(
                    "Monodoo Home could not save favorite applications",
                    error
                );
            }
        };

        this.favoriteSaveQueue = this.favoriteSaveQueue.then(save, save);
        return this.favoriteSaveQueue;
    }

    trackRecent(app) {
        if (!app.xmlid || app.xmlid === MONODOO_HOME_MENU_XMLID) {
            return;
        }
        this.state.recentXmlids = normalizeRecentApps(
            this.state.recentXmlids,
            app.xmlid
        );
        writeRecentApps(
            browser.localStorage,
            this.recentStorageKey,
            this.state.recentXmlids
        );
    }

    async openApp(app) {
        const result = await this.menuService.selectMenu(app);
        this.trackRecent(app);
        return result;
    }
}

registry.category("actions").add("monodoo_home", MonodooHome);
