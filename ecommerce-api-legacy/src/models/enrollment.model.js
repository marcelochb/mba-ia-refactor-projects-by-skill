'use strict';

const db = require('../config/database');

module.exports = {
    create(userId, courseId) {
        return db.run("INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)", [userId, courseId]);
    },
    removeByUser(userId) {
        return db.run("DELETE FROM enrollments WHERE user_id = ?", [userId]);
    },
    // Relatório financeiro numa única query com JOIN (elimina o N+1 do original).
    financialReport() {
        return db.all(
            `SELECT c.title AS course,
                    u.name  AS student,
                    p.amount AS amount,
                    p.status AS status
             FROM courses c
             LEFT JOIN enrollments e ON e.course_id = c.id
             LEFT JOIN users u ON u.id = e.user_id
             LEFT JOIN payments p ON p.enrollment_id = e.id
             ORDER BY c.id`,
            []
        );
    },
};
