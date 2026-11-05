// Logger mínimo com níveis. Nunca registre cartões, senhas ou chaves.
const logger = {
    info: (...args) => console.log('[INFO]', ...args),
    warn: (...args) => console.warn('[WARN]', ...args),
    error: (...args) => console.error('[ERROR]', ...args),
};

module.exports = logger;
