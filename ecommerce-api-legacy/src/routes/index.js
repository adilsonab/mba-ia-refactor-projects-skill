const express = require('express');
const { asyncHandler } = require('../middlewares/errorHandler');

// Matriz de acesso:
//   POST   /api/login                   público
//   POST   /api/checkout                público (e-mail existente exige pwd correto ou token do próprio usuário)
//   GET    /api/admin/financial-report  admin
//   DELETE /api/users/:id               admin
function buildRoutes({ controllers, auth }) {
    const { checkoutController, reportController, userController, authController } = controllers;
    const h = asyncHandler;
    const router = express.Router();

    router.post('/api/login', h(authController.login));
    router.post('/api/checkout', h(auth.optionalAuthenticate), h(checkoutController.checkout));
    router.get('/api/admin/financial-report', h(auth.authenticate), h(auth.requireAdmin), h(reportController.financialReport));
    router.delete('/api/users/:id', h(auth.authenticate), h(auth.requireAdmin), h(userController.deleteUser));

    return router;
}

module.exports = { buildRoutes };
