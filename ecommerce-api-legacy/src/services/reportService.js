const { PAYMENT_STATUS, UNKNOWN_STUDENT } = require('../config/constants');

function createReportService({ reportModel }) {
    return {
        async financialReport() {
            const rows = await reportModel.listCourseEnrollmentPayments();
            const byCourse = new Map();

            for (const row of rows) {
                if (!byCourse.has(row.course_id)) {
                    byCourse.set(row.course_id, { course: row.title, revenue: 0, students: [] });
                }
                if (row.enrollment_id === null) continue; // curso sem matrículas

                const entry = byCourse.get(row.course_id);
                const hasPayment = row.amount !== null;
                if (hasPayment && row.status === PAYMENT_STATUS.PAID) entry.revenue += row.amount;
                entry.students.push({
                    student: row.student ?? UNKNOWN_STUDENT,
                    paid: hasPayment ? row.amount : 0,
                });
            }

            return [...byCourse.values()];
        },
    };
}

module.exports = { createReportService };
