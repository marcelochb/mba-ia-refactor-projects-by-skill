'use strict';

const db = require('../config/database');
const userModel = require('../models/user.model');
const courseModel = require('../models/course.model');
const enrollmentModel = require('../models/enrollment.model');
const paymentModel = require('../models/payment.model');
const auditLog = require('../models/auditLog.model');
const paymentService = require('./payment.service');
const cache = require('./cache.service');
const { hashPassword } = require('./crypto.service');

class DomainError extends Error {
    constructor(message, status) {
        super(message);
        this.status = status;
    }
}

// Orquestra o checkout completo numa transação atômica.
async function checkout({ name, email, password, courseId, card }) {
    const course = await courseModel.findActiveById(courseId);
    if (!course) throw new DomainError('Curso não encontrado', 404);

    const status = paymentService.authorize(card);
    if (status === paymentService.STATUS_DENIED) {
        throw new DomainError('Pagamento recusado', 400);
    }

    let user = await userModel.findByEmail(email);

    await db.run('BEGIN');
    try {
        if (!user) {
            const created = await userModel.create(name, email, hashPassword(password || '123456'));
            user = { id: created.lastID };
        }
        const enrollment = await enrollmentModel.create(user.id, courseId);
        await paymentModel.create(enrollment.lastID, course.price, status);
        await auditLog.record(`Checkout curso ${courseId} por ${user.id}`);
        await db.run('COMMIT');

        cache.set(`last_checkout_${user.id}`, course.title);
        return { msg: 'Sucesso', enrollment_id: enrollment.lastID };
    } catch (err) {
        await db.run('ROLLBACK');
        throw err;
    }
}

module.exports = { checkout, DomainError };
