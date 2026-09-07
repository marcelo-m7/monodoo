export function normalizeRecentApps(currentXmlids, selectedXmlid, limit = 6) {
    const ordered = [];
    if (typeof selectedXmlid === "string" && selectedXmlid) {
        ordered.push(selectedXmlid);
    }
    for (const xmlid of Array.isArray(currentXmlids) ? currentXmlids : []) {
        if (typeof xmlid === "string" && xmlid && !ordered.includes(xmlid)) {
            ordered.push(xmlid);
        }
    }
    return ordered.slice(0, Math.max(0, limit));
}

export function getRecentStorageKey(database, userId) {
    return `monodoo:recent-apps:${database || "unknown"}:${userId || "anonymous"}`;
}

export function readRecentApps(storage, key) {
    try {
        const value = JSON.parse(storage?.getItem(key) || "[]");
        return Array.isArray(value) ? value.filter((item) => typeof item === "string" && item) : [];
    } catch {
        return [];
    }
}

export function writeRecentApps(storage, key, xmlids) {
    try {
        storage?.setItem(key, JSON.stringify(xmlids));
    } catch {
        // Recents are a non-critical browser preference.
    }
}
