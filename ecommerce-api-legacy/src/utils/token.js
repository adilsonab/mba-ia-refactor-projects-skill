const crypto = require('crypto');

const b64 = (value) => Buffer.from(value).toString('base64url');
const sign = (body, secret) => crypto.createHmac('sha256', secret).update(body).digest();

// Token "<payload>.<assinatura>" com HMAC-SHA256 e expiração (exp em segundos).
function signToken(payload, secret, ttlSeconds) {
    const body = b64(JSON.stringify({ ...payload, exp: Math.floor(Date.now() / 1000) + ttlSeconds }));
    return `${body}.${b64(sign(body, secret))}`;
}

function verifyToken(token, secret) {
    const [body, signature, extra] = String(token || '').split('.');
    if (!body || !signature || extra !== undefined) return null;
    const expected = sign(body, secret);
    const given = Buffer.from(signature, 'base64url');
    if (given.length !== expected.length || !crypto.timingSafeEqual(given, expected)) return null;
    try {
        const payload = JSON.parse(Buffer.from(body, 'base64url').toString('utf8'));
        return typeof payload.exp === 'number' && payload.exp > Date.now() / 1000 ? payload : null;
    } catch {
        return null;
    }
}

module.exports = { signToken, verifyToken };
