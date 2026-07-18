'use strict';

const db = require('../config/database');
const userModel = require('../models/user.model');
const enrollmentModel = require('../models/enrollment.model');
const paymentModel = require('../models/payment.model');

// Exclusão de usuário em cascata dentro de transação (sem registros órfãos).
async function deleteUser(userId) {
    await db.run('BEGIN');
    try {
        await paymentModel.removeByEnrollmentUser(userId);
        await enrollmentModel.removeByUser(userId);
        await userModel.remove(userId);
        await db.run('COMMIT');
    } catch (err) {
        await db.run('ROLLBACK');
        throw err;
    }
}

module.exports = { deleteUser };
