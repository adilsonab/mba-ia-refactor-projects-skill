const crypto = require('crypto');

const KEY_LENGTH = 64;

function hashPassword(raw) {
    const salt = crypto.randomBytes(16).toString('hex');
    const hash = crypto.scryptSync(String(raw), salt, KEY_LENGTH).toString('hex');
    return `scrypt$${salt}$${hash}`;
}

// Usado quando o cliente não envia senha: nunca aplicar uma senha padrão conhecida.
function randomPassword() {
    return crypto.randomBytes(12).toString('hex');
}

module.exports = { hashPassword, randomPassword };
