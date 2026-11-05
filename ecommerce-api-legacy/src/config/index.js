const logger = require('../utils/logger');

const config = {
    port: Number(process.env.PORT) || 3000,
    databasePath: process.env.DATABASE_PATH || ':memory:',
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
};

if (!config.paymentGatewayKey) {
    logger.warn('PAYMENT_GATEWAY_KEY não definida; gateway de pagamento roda em modo simulado (apenas desenvolvimento).');
}

module.exports = config;
