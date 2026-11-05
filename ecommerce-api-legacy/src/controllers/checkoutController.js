const { ValidationError } = require('../middlewares/errorHandler');

const isNonEmptyString = (value) => typeof value === 'string' && value.length > 0;
const isValidCourseId = (value) => (typeof value === 'number' && Number.isFinite(value))
    || isNonEmptyString(value);

function createCheckoutController({ checkoutService }) {
    return {
        async checkout(req, res) {
            const body = req.body ?? {};
            // Nomes externos (contrato) → nomes internos claros.
            const { usr: name, eml: email, pwd: password, c_id: courseId, card: cardNumber } = body;

            if (!name || !email || !courseId || !cardNumber) throw new ValidationError();
            if (!isNonEmptyString(name) || !isNonEmptyString(email) || !isValidCourseId(courseId)
                || !isNonEmptyString(cardNumber)) {
                throw new ValidationError();
            }
            if (password !== undefined && password !== null && typeof password !== 'string') {
                throw new ValidationError();
            }

            const enrollmentId = await checkoutService.checkout({ name, email, password, courseId, cardNumber });
            res.status(200).json({ msg: 'Sucesso', enrollment_id: enrollmentId });
        },
    };
}

module.exports = { createCheckoutController };
