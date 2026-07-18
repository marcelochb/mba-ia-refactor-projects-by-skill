'use strict';

const userService = require('../services/user.service');

async function remove(req, res, next) {
    try {
        await userService.deleteUser(req.params.id);
        res.json({ msg: 'Usuário e dados relacionados removidos com sucesso' });
    } catch (err) {
        next(err);
    }
}

module.exports = { remove };
