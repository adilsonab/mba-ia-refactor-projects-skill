const { ValidationError } = require('../middlewares/errorHandler');
const { parsePositiveId } = require('./validators');

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const CARD_PATTERN = /^\d{12,19}$/; // somente dígitos (PAN de 12 a 19 posições)

const isNonEmptyString = (value) => typeof value === 'string' && value.trim().length > 0;

function createCheckoutController({ checkoutService }) {
    return {
        async checkout(req, res) {
            const body = req.body ?? {};
            // Nomes externos (contrato) → nomes internos claros.
            const { usr: name, eml: email, pwd: password, c_id: rawCourseId, card: cardNumber } = body;

            if (!name || !email || !rawCourseId || !cardNumber) throw new ValidationError();
            if (!isNonEmptyString(name)) throw new ValidationError();
            if (typeof email !== 'string' || !EMAIL_PATTERN.test(email)) throw new ValidationError();
            if (typeof cardNumber !== 'string' || !CARD_PATTERN.test(cardNumber)) throw new ValidationError();
            if (password !== undefined && password !== null && typeof password !== 'string') {
                throw new ValidationError();
            }
            const courseId = parsePositiveId(rawCourseId); // 2 ou "2"; qualquer outra coisa → 400

            const enrollmentId = await checkoutService.checkout({ name, email, password, courseId, cardNumber });
            res.status(200).json({ msg: 'Sucesso', enrollment_id: enrollmentId });
        },
    };
}

module.exports = { createCheckoutController };
