const { PAYMENT_STATUS } = require('../config/constants');

function createReportService({ reportModel }) {
    // Formato preservado: [{ course, revenue, students: [{ student, paid }] }]
    async function financialReport() {
        const rows = await reportModel.financialRows();
        const byCourse = new Map();
        for (const row of rows) {
            if (!byCourse.has(row.course_id)) byCourse.set(row.course_id, { course: row.title, revenue: 0, students: [] });
            if (row.enrollment_id === null) continue;
            const entry = byCourse.get(row.course_id);
            if (row.status === PAYMENT_STATUS.PAID) entry.revenue += row.amount;
            entry.students.push({ student: row.student ?? 'Unknown', paid: row.amount ?? 0 });
        }
        return [...byCourse.values()];
    }

    return { financialReport };
}

module.exports = { createReportService };
