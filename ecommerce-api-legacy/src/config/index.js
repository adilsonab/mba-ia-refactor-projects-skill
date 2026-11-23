const crypto = require('crypto');

const csv = (value) => (value || '').split(',').map((item) => item.trim()).filter(Boolean);
const positiveInt = (value, fallback) => {
    const parsed = Number.parseInt(value, 10);
    return Number.isInteger(parsed) && parsed > 0 ? parsed : fallback;
};

const warnings = [];
let secretKey = process.env.SECRET_KEY;
if (!secretKey) {
    secretKey = crypto.randomBytes(32).toString('hex');
    warnings.push('SECRET_KEY não definida; usando chave aleatória por boot (tokens expiram ao reiniciar — apenas desenvolvimento).');
}

module.exports = {
    port: positiveInt(process.env.PORT, 3000),
    host: process.env.HOST || '127.0.0.1', // expor na rede exige HOST=0.0.0.0 explícito
    corsOrigins: csv(process.env.CORS_ORIGINS), // [] = CORS fechado
    secretKey,
    tokenTtlSeconds: positiveInt(process.env.TOKEN_TTL_SECONDS, 3600),
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
    adminEmail: process.env.ADMIN_EMAIL || 'admin@fullcycle.com.br',
    adminPassword: process.env.ADMIN_PASSWORD || '',
    logLevel: process.env.LOG_LEVEL || 'info',
    warnings,
};
