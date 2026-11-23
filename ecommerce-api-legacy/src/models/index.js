const { createUserModel } = require('./userModel');
const { createCourseModel } = require('./courseModel');
const { createEnrollmentModel } = require('./enrollmentModel');
const { createPaymentModel } = require('./paymentModel');
const { createAuditLogModel } = require('./auditLogModel');
const { createReportModel } = require('./reportModel');

function createModels(db) {
    return {
        userModel: createUserModel(db),
        courseModel: createCourseModel(db),
        enrollmentModel: createEnrollmentModel(db),
        paymentModel: createPaymentModel(db),
        auditLogModel: createAuditLogModel(db),
        reportModel: createReportModel(db),
    };
}

module.exports = { createModels };
