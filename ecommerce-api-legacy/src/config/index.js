const logger = require('../utils/logger');

const config = {
    port: Number(process.env.PORT) || 3000,
    databasePath: process.env.DATABASE_PATH || ':memory:',
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
    // Credencial das rotas administrativas (Authorization: Bearer <ADMIN_TOKEN>). Nunca versionar.
    adminToken: process.env.ADMIN_TOKEN || '',
};

if (!config.paymentGatewayKey) {
    logger.warn('PAYMENT_GATEWAY_KEY não definida; gateway de pagamento roda em modo simulado (apenas desenvolvimento).');
}
if (!config.adminToken) {
    logger.warn('ADMIN_TOKEN não definida; rotas administrativas desabilitadas (respondem 401).');
}

module.exports = config;
