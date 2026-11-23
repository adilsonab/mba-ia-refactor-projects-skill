const { signToken, verifyToken } = require('../utils/token');
const { verifyPassword } = require('../utils/password');
const { unauthorized } = require('../utils/errors');

const INVALID_CREDENTIALS = 'Credenciais inválidas';

function createAuthService({ userModel, config }) {
    // Retorna o usuário (sem hash) se e-mail/senha conferem, senão null.
    async function checkCredentials(email, password) {
        const record = await userModel.findCredentialsByEmail(email);
        if (!record || !(await verifyPassword(record.pass, password))) return null;
        const { pass, ...user } = record;
        return user;
    }

    async function login(email, password) {
        const user = await checkCredentials(email, password);
        if (!user) throw unauthorized(INVALID_CREDENTIALS);
        return signToken({ uid: user.id }, config.secretKey, config.tokenTtlSeconds);
    }

    // Papel e existência relidos do banco a cada requisição; token carrega só o id.
    async function userFromToken(token) {
        const payload = verifyToken(token, config.secretKey);
        if (!payload || !Number.isInteger(payload.uid)) return null;
        return (await userModel.findById(payload.uid)) || null;
    }

    return { checkCredentials, login, userFromToken, INVALID_CREDENTIALS };
}

module.exports = { createAuthService };
