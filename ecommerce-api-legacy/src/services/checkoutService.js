const { PAYMENT_STATUS } = require('../config/constants');
const { AppError, NotFoundError } = require('../middlewares/errorHandler');
const { hashPassword, randomPassword } = require('../utils/password');

function createCheckoutService({ db, userModel, courseModel, enrollmentModel, paymentModel, auditLogModel, paymentGateway }) {
    return {
        async checkout({ name, email, password, courseId, cardNumber }) {
            const course = await courseModel.findActiveById(courseId);
            if (!course) throw new NotFoundError('Curso não encontrado');

            // Usuário, matrícula, pagamento e auditoria são atômicos: pagamento recusado ou
            // falha de escrita desfaz tudo (sem matrícula sem pagamento nem usuário órfão).
            return db.transaction(async () => {
                const existing = await userModel.findByEmail(email);
                const userId = existing
                    ? existing.id
                    : await userModel.create({ name, email, passwordHash: hashPassword(password || randomPassword()) });

                const status = paymentGateway.charge(cardNumber, course.price);
                if (status !== PAYMENT_STATUS.PAID) throw new AppError('Pagamento recusado', 400);

                const enrollmentId = await enrollmentModel.create(userId, course.id);
                await paymentModel.create(enrollmentId, course.price, status);
                await auditLogModel.log(`Checkout curso ${course.id} por ${userId}`);
                return enrollmentId;
            });
        },
    };
}

module.exports = { createCheckoutService };
