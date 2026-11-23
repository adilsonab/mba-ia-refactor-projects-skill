const PAYMENT_STATUS = Object.freeze({ PAID: 'PAID', DENIED: 'DENIED' });

// Regra do gateway simulado (inalterada): cartões iniciados em "4" são aprovados.
const APPROVED_CARD_PREFIX = '4';

const ROLES = Object.freeze({ ADMIN: 'admin', STUDENT: 'student' });
const DEFAULT_ROLE = ROLES.STUDENT;

const CARD_NUMBER_PATTERN = /^\d{13,19}$/;
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const POSITIVE_INT_PATTERN = /^[1-9]\d*$/;

const CACHE_MAX_ENTRIES = 1000;
const GENERATED_PASSWORD_BYTES = 12;

module.exports = {
    PAYMENT_STATUS,
    APPROVED_CARD_PREFIX,
    ROLES,
    DEFAULT_ROLE,
    CARD_NUMBER_PATTERN,
    EMAIL_PATTERN,
    POSITIVE_INT_PATTERN,
    CACHE_MAX_ENTRIES,
    GENERATED_PASSWORD_BYTES,
};
