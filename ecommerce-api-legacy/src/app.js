const express = require('express');
const config = require('./config');
const logger = require('./utils/logger');
const { createDatabase } = require('./database');
const { createUserModel } = require('./models/userModel');
const { createCourseModel } = require('./models/courseModel');
const { createEnrollmentModel } = require('./models/enrollmentModel');
const { createPaymentModel } = require('./models/paymentModel');
const { createAuditLogModel } = require('./models/auditLogModel');
const { createReportModel } = require('./models/reportModel');
const { createPaymentGateway } = require('./services/paymentGateway');
const { createCheckoutService } = require('./services/checkoutService');
const { createReportService } = require('./services/reportService');
const { createUserService } = require('./services/userService');
const { createCheckoutController } = require('./controllers/checkoutController');
const { createReportController } = require('./controllers/reportController');
const { createUserController } = require('./controllers/userController');
const { buildRoutes } = require('./routes');
const { errorHandler } = require('./middlewares/errorHandler');

// Composition root: cria as dependências e as injeta camada por camada.
function createApp(db) {
    const userModel = createUserModel(db);
    const courseModel = createCourseModel(db);
    const enrollmentModel = createEnrollmentModel(db);
    const paymentModel = createPaymentModel(db);
    const auditLogModel = createAuditLogModel(db);
    const reportModel = createReportModel(db);

    const paymentGateway = createPaymentGateway({ apiKey: config.paymentGatewayKey, logger });
    const checkoutService = createCheckoutService({
        db, userModel, courseModel, enrollmentModel, paymentModel, auditLogModel, paymentGateway,
    });
    const reportService = createReportService({ reportModel });
    const userService = createUserService({ db, userModel });

    const app = express();
    app.use(express.json());
    app.use(buildRoutes({
        checkoutController: createCheckoutController({ checkoutService }),
        reportController: createReportController({ reportService }),
        userController: createUserController({ userService }),
    }));
    app.use(errorHandler);
    return app;
}

async function main() {
    const db = await createDatabase(config.databasePath);
    const app = createApp(db);
    app.listen(config.port, () => {
        logger.info(`Frankenstein LMS rodando na porta ${config.port}...`);
    });
}

if (require.main === module) {
    main().catch((err) => {
        logger.error('Falha ao iniciar a aplicação:', err);
        process.exit(1);
    });
}

module.exports = { createApp };
