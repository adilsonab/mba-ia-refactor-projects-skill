const { checkoutPayload } = require('../utils/validators');

function createCheckoutController({ checkoutService }) {
    return {
        async checkout(req, res) {
            const input = checkoutPayload(req); // mapeia usr/eml/pwd/c_id/card
            const { enrollmentId } = await checkoutService.checkout(input, req.user || null);
            res.status(200).json({ msg: 'Sucesso', enrollment_id: enrollmentId });
        },
    };
}

module.exports = { createCheckoutController };
