const { ValidationError } = require('../middlewares/errorHandler');

// Aceita 2 ou "2" (o contrato original aceitava os dois); qualquer outro valor → 400.
function parsePositiveId(value) {
    const text = typeof value === 'number' ? String(value) : value;
    if (typeof text !== 'string' || !/^[1-9]\d*$/.test(text.trim())) throw new ValidationError();
    return Number(text.trim());
}

module.exports = { parsePositiveId };
