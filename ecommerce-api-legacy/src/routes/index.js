const express = require('express');
const { asyncHandler } = require('../middlewares/errorHandler');

function buildRoutes({ checkoutController, reportController, userController }) {
    const router = express.Router();

    router.post('/api/checkout', asyncHandler(checkoutController.checkout));
    router.get('/api/admin/financial-report', asyncHandler(reportController.financialReport));
    router.delete('/api/users/:id', asyncHandler(userController.deleteUser));

    return router;
}

module.exports = { buildRoutes };
