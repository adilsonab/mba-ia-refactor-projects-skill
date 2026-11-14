const crypto = require('crypto');
const { UnauthorizedError } = require('./errorHandler');

// Extrai o token de "Authorization: Bearer <token>".
function bearerToken(req) {
    const [scheme, token] = (req.get('authorization') || '').split(' ');
    return scheme && scheme.toLowerCase() === 'bearer' && token ? token.trim() : '';
}

function safeEqual(given, expected) {
    const a = Buffer.from(given);
    const b = Buffer.from(expected);
    return a.length === b.length && crypto.timingSafeEqual(a, b);
}

// O projeto não tem login nem papéis: a credencial de administrador é definida no servidor
// (ADMIN_TOKEN). Sem a variável, as rotas administrativas ficam desabilitadas (401).
function createRequireAdmin({ adminToken }) {
    return function requireAdmin(req, res, next) {
        if (!adminToken || !safeEqual(bearerToken(req), adminToken)) {
            return next(new UnauthorizedError());
        }
        return next();
    };
}

module.exports = { createRequireAdmin };
