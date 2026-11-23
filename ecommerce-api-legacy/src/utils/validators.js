const { badRequest } = require('./errors');
const { CARD_NUMBER_PATTERN, EMAIL_PATTERN, POSITIVE_INT_PATTERN } = require('../config/constants');

const isNonEmptyString = (value) => typeof value === 'string' && value.trim() !== '';

function requireBody(req) {
    const body = req.body;
    if (!body || typeof body !== 'object' || Array.isArray(body)) throw badRequest();
    return body;
}

function parsePositiveInt(value) {
    if (typeof value === 'number' && Number.isInteger(value) && value > 0) return value;
    if (typeof value === 'string' && POSITIVE_INT_PATTERN.test(value)) return Number(value);
    throw badRequest();
}

function parseEmail(value) {
    if (!isNonEmptyString(value) || !EMAIL_PATTERN.test(value.trim())) throw badRequest();
    return value.trim().toLowerCase();
}

function parseOptionalPassword(value) {
    if (value === undefined || value === null || value === '') return null;
    if (typeof value !== 'string') throw badRequest();
    return value;
}

// Contrato externo: { usr, eml, pwd?, c_id, card }
function checkoutPayload(req) {
    const body = requireBody(req);
    const { usr, eml, pwd, c_id: courseId, card } = body;
    if (!isNonEmptyString(usr) || !eml || !courseId || !card) throw badRequest();
    if (typeof card !== 'string' || !CARD_NUMBER_PATTERN.test(card)) throw badRequest();
    return {
        name: usr.trim(),
        email: parseEmail(eml),
        password: parseOptionalPassword(pwd),
        courseId: parsePositiveInt(courseId),
        cardNumber: card,
    };
}

// Contrato do login: { eml, pwd }
function loginPayload(req) {
    const { eml, pwd } = requireBody(req);
    if (typeof pwd !== 'string' || pwd === '') throw badRequest();
    return { email: parseEmail(eml), password: pwd };
}

module.exports = { checkoutPayload, loginPayload, parsePositiveInt };
