'use strict';

const db = require('../config/database');

module.exports = {
    record(action) {
        return db.run("INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))", [action]);
    },
};
