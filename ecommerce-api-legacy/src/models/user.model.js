'use strict';

const db = require('../config/database');

module.exports = {
    findByEmail(email) {
        return db.get("SELECT * FROM users WHERE email = ?", [email]);
    },
    create(name, email, passHash) {
        return db.run("INSERT INTO users (name, email, pass) VALUES (?, ?, ?)", [name, email, passHash]);
    },
    remove(id) {
        return db.run("DELETE FROM users WHERE id = ?", [id]);
    },
};
