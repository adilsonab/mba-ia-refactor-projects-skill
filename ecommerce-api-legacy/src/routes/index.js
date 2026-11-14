const express = require('express');
const { asyncHandler } = require('../middlewares/errorHandler');

// Matriz de acesso: checkout é o fluxo público de compra; relatório financeiro e exclusão
// de usuário são administrativos (requireAdmin).
function buildRoutes({ checkoutController, reportController, userController, requireAdmin }) {
    const router = express.Router();

    router.post('/api/checkout', asyncHandler(checkoutController.checkout));
    router.get('/api/admin/financial-report', requireAdmin, asyncHandler(reportController.financialReport));
    router.delete('/api/users/:id', requireAdmin, asyncHandler(userController.deleteUser));

    return router;
}

module.exports = { buildRoutes };
