import { patch } from "@web/core/utils/patch";
import { WebClient } from "@web/webclient/webclient";

import { MonodooAppsBar } from "../appsbar/appsbar";

patch(WebClient, {
    components: {
        ...WebClient.components,
        AppsBar: MonodooAppsBar,
    },
});
