'use strict';

const enrollmentModel = require('../models/enrollment.model');

// Monta o relatório financeiro a partir da query única com JOIN.
// Preserva o formato de saída do endpoint original.
async function financialReport() {
    const rows = await enrollmentModel.financialReport();
    const byCourse = new Map();

    for (const row of rows) {
        if (!byCourse.has(row.course)) {
            byCourse.set(row.course, { course: row.course, revenue: 0, students: [] });
        }
        const data = byCourse.get(row.course);
        if (row.student) {
            if (row.status === 'PAID') data.revenue += row.amount;
            data.students.push({ student: row.student, paid: row.amount || 0 });
        }
    }

    return Array.from(byCourse.values());
}

module.exports = { financialReport };
