const crypto = require('crypto');
const { promisify } = require('util');
const { GENERATED_PASSWORD_BYTES } = require('../config/constants');

const scrypt = promisify(crypto.scrypt);
const KEY_LENGTH = 64;

async function hashPassword(raw) {
    const salt = crypto.randomBytes(16).toString('hex');
    const hash = await scrypt(String(raw), salt, KEY_LENGTH);
    return `scrypt$${salt}$${hash.toString('hex')}`;
}

async function verifyPassword(stored, raw) {
    const [algo, salt, hash] = String(stored || '').split('$');
    if (algo !== 'scrypt' || !salt || !hash || typeof raw !== 'string') return false;
    const expected = Buffer.from(hash, 'hex');
    const candidate = await scrypt(raw, salt, expected.length);
    return expected.length === candidate.length && crypto.timingSafeEqual(candidate, expected);
}

// Usada quando o checkout não recebe senha: nunca é logada nem devolvida.
const generatePassword = () => crypto.randomBytes(GENERATED_PASSWORD_BYTES).toString('hex');

module.exports = { hashPassword, verifyPassword, generatePassword };
