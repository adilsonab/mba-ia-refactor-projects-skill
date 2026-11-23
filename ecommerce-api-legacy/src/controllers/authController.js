const { loginPayload } = require('../utils/validators');

function createAuthController({ authService }) {
    return {
        async login(req, res) {
            const { email, password } = loginPayload(req);
            res.status(200).json({ token: await authService.login(email, password) });
        },
    };
}

module.exports = { createAuthController };
