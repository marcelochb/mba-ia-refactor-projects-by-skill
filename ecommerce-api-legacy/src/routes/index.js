'use strict';

const express = require('express');
const checkoutController = require('../controllers/checkout.controller');
const reportController = require('../controllers/report.controller');
const userController = require('../controllers/user.controller');
const { validateCheckout } = require('../middlewares/validation');

const router = express.Router();

router.post('/checkout', validateCheckout, checkoutController.checkout);
router.get('/admin/financial-report', reportController.financialReport);
router.delete('/users/:id', userController.remove);

module.exports = router;
