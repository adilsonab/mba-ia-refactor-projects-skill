const express = require('express');
const config = require('./config');
const { createLogger } = require('./utils/logger');
const { createDatabase } = require('./database');
const { seed } = require('./database/seed');
const { createModels } = require('./models');
const { createPaymentGateway } = require('./services/paymentGateway');
const { createCacheService } = require('./services/cacheService');
const { createAuthService } = require('./services/authService');
const { createCheckoutService } = require('./services/checkoutService');
const { createReportService } = require('./services/reportService');
const { createUserService } = require('./services/userService');
const { createCheckoutController } = require('./controllers/checkoutController');
const { createReportController } = require('./controllers/reportController');
const { createUserController } = require('./controllers/userController');
const { createAuthController } = require('./controllers/authController');
const { createAuthMiddleware } = require('./middlewares/auth');
const { createCors } = require('./middlewares/cors');
const { createErrorHandler } = require('./middlewares/errorHandler');
const { buildRoutes } = require('./routes');

// Composition root: cria dependências e as injeta nas camadas.
async function createApp(logger) {
    const db = await createDatabase();
    await seed(db, config, logger);

    const models = createModels(db);
    const paymentGateway = createPaymentGateway({ apiKey: config.paymentGatewayKey, logger });
    const cache = createCacheService({ logger });
    const authService = createAuthService({ userModel: models.userModel, config });
    const checkoutService = createCheckoutService({ db, models, paymentGateway, cache, logger, authService });
    const reportService = createReportService({ reportModel: models.reportModel });
    const userService = createUserService({ db, models });

    const controllers = {
        checkoutController: createCheckoutController({ checkoutService }),
        reportController: createReportController({ reportService }),
        userController: createUserController({ userService }),
        authController: createAuthController({ authService }),
    };

    const app = express();
    app.disable('x-powered-by');
    app.use(createCors(config.corsOrigins));
    app.use(express.json());
    app.use(buildRoutes({ controllers, auth: createAuthMiddleware({ authService }) }));
    app.use(createErrorHandler(logger));
    return app;
}

async function main(logger) {
    config.warnings.forEach((message) => logger.warn(message));
    if (!config.paymentGatewayKey) logger.warn('PAYMENT_GATEWAY_KEY não definida (gateway simulado).');

    const app = await createApp(logger);
    app.listen(config.port, config.host, () => {
        const cors = config.corsOrigins.length ? config.corsOrigins.join(', ') : 'fechado';
        logger.info(`LMS API rodando em http://${config.host}:${config.port} (CORS: ${cors})`);
    });
}

if (require.main === module) {
    const logger = createLogger(config.logLevel);
    main(logger).catch((err) => {
        logger.error('Falha ao iniciar a aplicação:', err && err.stack ? err.stack : err);
        process.exit(1);
    });
}

module.exports = { createApp };
