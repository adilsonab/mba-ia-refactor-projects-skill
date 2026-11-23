const { unauthorized, forbidden } = require('../utils/errors');
const { ROLES } = require('../config/constants');

const bearerToken = (req) => {
    const [scheme, token] = (req.get('authorization') || '').split(' ');
    return scheme && scheme.toLowerCase() === 'bearer' && token ? token.trim() : null;
};

function createAuthMiddleware({ authService }) {
    // Exige token válido; usuário (e papel) recarregado do banco.
    async function authenticate(req, res, next) {
        const token = bearerToken(req);
        const user = token ? await authService.userFromToken(token) : null;
        if (!user) throw unauthorized('Autenticação necessária');
        req.user = user;
        next();
    }

    // Token opcional (checkout público): se presente, precisa ser válido.
    async function optionalAuthenticate(req, res, next) {
        if (!req.get('authorization')) return next();
        return authenticate(req, res, next);
    }

    function requireAdmin(req, res, next) {
        if (!req.user || req.user.role !== ROLES.ADMIN) throw forbidden('Acesso restrito a administradores');
        next();
    }

    return { authenticate, optionalAuthenticate, requireAdmin };
}

module.exports = { createAuthMiddleware };
