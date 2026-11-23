const { CACHE_MAX_ENTRIES } = require('../config/constants');

// Cache com escopo de instância e limite de entradas (substitui o globalCache de módulo).
function createCacheService({ maxEntries = CACHE_MAX_ENTRIES, logger } = {}) {
    const store = new Map();
    return {
        set(key, value) {
            store.delete(key);
            store.set(key, value);
            if (store.size > maxEntries) store.delete(store.keys().next().value);
            if (logger) logger.debug(`Cache atualizado: ${key}`);
        },
        get: (key) => store.get(key),
    };
}

module.exports = { createCacheService };
