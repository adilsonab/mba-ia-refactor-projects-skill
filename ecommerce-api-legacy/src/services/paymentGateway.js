const { PAYMENT_STATUS, APPROVED_CARD_PREFIX } = require('../config/constants');

// Gateway simulado, injetável (substituível por uma integração real ou por um mock em testes).
function createPaymentGateway({ apiKey, logger }) {
    return {
        charge(cardNumber, amount) {
            logger.info(`Processando pagamento de ${amount} com cartão final ${cardNumber.slice(-4)}`
                + ` (gateway ${apiKey ? 'configurado' : 'simulado'})`);
            return cardNumber.startsWith(APPROVED_CARD_PREFIX) ? PAYMENT_STATUS.PAID : PAYMENT_STATUS.DENIED;
        },
    };
}

module.exports = { createPaymentGateway };
