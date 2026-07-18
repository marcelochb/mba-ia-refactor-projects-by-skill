'use strict';

const reportService = require('../services/report.service');

async function financialReport(req, res, next) {
    try {
        const report = await reportService.financialReport();
        res.json(report);
    } catch (err) {
        next(err);
    }
}

module.exports = { financialReport };
