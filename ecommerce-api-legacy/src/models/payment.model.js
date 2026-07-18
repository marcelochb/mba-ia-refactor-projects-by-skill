'use strict';

const db = require('../config/database');

module.exports = {
    create(enrollmentId, amount, status) {
        return db.run("INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)", [enrollmentId, amount, status]);
    },
    removeByEnrollmentUser(userId) {
        return db.run(
            "DELETE FROM payments WHERE enrollment_id IN (SELECT id FROM enrollments WHERE user_id = ?)",
            [userId]
        );
    },
};
