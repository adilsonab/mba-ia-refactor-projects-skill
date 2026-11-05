const logger = require('../utils/logger');

class AppError extends Error {
    constructor(message, status = 400) {
        super(message);
        this.status = status;
    }
}

class ValidationError extends AppError {
    constructor(message = 'Bad Request') { super(message, 400); }
}

class NotFoundError extends AppError {
    constructor(message) { super(message, 404); }
}

const asyncHandler = (fn) => (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);

// eslint-disable-next-line no-unused-vars
function errorHandler(err, req, res, next) {
    // Mantém o formato original da API: erros em texto puro.
    if (err instanceof AppError) return res.status(err.status).send(err.message);
    if (err.type === 'entity.parse.failed') return res.status(400).send('Bad Request');

    logger.error(`${req.method} ${req.originalUrl} falhou:`, err);
    return res.status(500).send('Erro interno');
}

module.exports = { AppError, ValidationError, NotFoundError, asyncHandler, errorHandler };
