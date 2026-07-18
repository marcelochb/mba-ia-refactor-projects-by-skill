'use strict';

const db = require('../config/database');

module.exports = {
    findActiveById(id) {
        return db.get("SELECT * FROM courses WHERE id = ? AND active = 1", [id]);
    },
    findAll() {
        return db.all("SELECT * FROM courses", []);
    },
};
