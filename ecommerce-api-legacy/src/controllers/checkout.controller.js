'use strict';

const checkoutService = require('../services/checkout.service');

// Controller fino: recebe input já validado, delega ao service, responde.
async function checkout(req, res, next) {
    try {
        const result = await checkoutService.checkout(req.checkout);
        res.status(200).json(result);
    } catch (err) {
        next(err);
    }
}

module.exports = { checkout };
