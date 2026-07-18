'use strict';

// Validação de input na borda para o checkout.
function validateCheckout(req, res, next) {
    const { usr, eml, c_id, card } = req.body || {};
    if (!usr || !eml || !c_id || !card) {
        return res.status(400).send('Bad Request');
    }
    const emailOk = /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(eml);
    if (!emailOk) return res.status(400).send('Email inválido');
    if (!/^\d{4,19}$/.test(String(card))) return res.status(400).send('Cartão inválido');

    req.checkout = {
        name: usr,
        email: eml,
        password: req.body.pwd,
        courseId: c_id,
        card: String(card),
    };
    next();
}

module.exports = { validateCheckout };
