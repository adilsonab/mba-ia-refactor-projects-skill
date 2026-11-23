const { HttpError } = require('../utils/errors');

// Encaminha rejeições de handlers async ao error handler central.
const asyncHandler = (fn) => (req, res, next) => Promise.resolve().then(() => fn(req, res, next)).catch(next);

function createErrorHandler(logger) {
    // eslint-disable-next-line no-unused-vars
    return (err, req, res, next) => {
        if (err instanceof HttpError) return res.status(err.status).send(err.message);
        if (err && err.type === 'entity.parse.failed') return res.status(400).send('Bad Request');
        logger.error(`Erro não tratado em ${req.method} ${req.path}:`, err && err.stack ? err.stack : err);
        return res.status(500).send('Erro interno');
    };
}

module.exports = { asyncHandler, createErrorHandler };
