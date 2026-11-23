const { PAYMENT_STATUS, APPROVED_CARD_PREFIX } = require('../config/constants');

// Gateway simulado (mesma regra do código original), injetável e substituível.
function createPaymentGateway({ apiKey, logger }) {
    return {
        apiKey, // usada por um gateway real; nunca logada
        charge(cardNumber, amount) {
            const status = cardNumber.startsWith(APPROVED_CARD_PREFIX) ? PAYMENT_STATUS.PAID : PAYMENT_STATUS.DENIED;
            logger.info(`Processando pagamento de ${amount} com cartão **** ${cardNumber.slice(-4)}: ${status}`);
            return status;
        },
    };
}

module.exports = { createPaymentGateway };
