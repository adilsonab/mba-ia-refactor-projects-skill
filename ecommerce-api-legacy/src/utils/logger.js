const LEVELS = { debug: 10, info: 20, warn: 30, error: 40 };

function createLogger(level = 'info') {
    const threshold = LEVELS[level] ?? LEVELS.info;
    const emit = (name, stream) => (...args) => {
        if (LEVELS[name] < threshold) return;
        stream(`${new Date().toISOString()} [${name.toUpperCase()}]`, ...args);
    };
    return {
        debug: emit('debug', console.log),
        info: emit('info', console.log),
        warn: emit('warn', console.warn),
        error: emit('error', console.error),
    };
}

module.exports = { createLogger };
