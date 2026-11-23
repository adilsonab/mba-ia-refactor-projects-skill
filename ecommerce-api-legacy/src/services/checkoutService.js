const { PAYMENT_STATUS, DEFAULT_ROLE } = require('../config/constants');
const { HttpError, notFound, unauthorized } = require('../utils/errors');
const { hashPassword, generatePassword, verifyPassword } = require('../utils/password');

function createCheckoutService({ db, models, paymentGateway, cache, logger, authService }) {
    const { courseModel, userModel, enrollmentModel, paymentModel, auditLogModel } = models;

    // Identifica o comprador. E-mail existente exige senha correta ou token do próprio usuário.
    async function resolveExistingBuyer(record, password, requester) {
        if (requester && requester.id === record.id) return record.id;
        if (password && (await verifyPassword(record.pass, password))) return record.id;
        throw unauthorized(authService.INVALID_CREDENTIALS);
    }

    async function checkout({ name, email, password, courseId, cardNumber }, requester = null) {
        const course = await courseModel.findActiveById(courseId);
        if (!course) throw notFound('Curso não encontrado');

        const { userId, enrollmentId } = await db.transaction(async () => {
            const existing = await userModel.findCredentialsByEmail(email);
            const existingUserId = existing ? await resolveExistingBuyer(existing, password, requester) : null;

            // Pagamento decidido antes de qualquer escrita: recusa não deixa dados parciais.
            const status = paymentGateway.charge(cardNumber, course.price);
            if (status !== PAYMENT_STATUS.PAID) throw new HttpError(400, 'Pagamento recusado');

            const userId = existingUserId ?? await userModel.create({
                name,
                email,
                passwordHash: await hashPassword(password || generatePassword()),
                role: DEFAULT_ROLE, // papel sempre definido pelo servidor
            });
            const enrollmentId = await enrollmentModel.create(userId, course.id);
            await paymentModel.create(enrollmentId, course.price, status);
            await auditLogModel.log(`Checkout curso ${course.id} por ${userId}`);
            return { userId, enrollmentId };
        });

        cache.set(`last_checkout_${userId}`, course.title);
        logger.info(`Checkout concluído: matrícula ${enrollmentId} (curso ${course.id}, usuário ${userId})`);
        return { enrollmentId };
    }

    return { checkout };
}

module.exports = { createCheckoutService };
