'use strict';

const crypto = require('crypto');

// Hash de senha com scrypt (algoritmo forte da lib padrão do Node) + salt aleatório.
// Substitui o `badCrypto` caseiro do projeto original.
function hashPassword(plain) {
    const salt = crypto.randomBytes(16).toString('hex');
    const derived = crypto.scryptSync(plain, salt, 64).toString('hex');
    return `${salt}:${derived}`;
}

function verifyPassword(plain, stored) {
    if (!stored || !stored.includes(':')) return false;
    const [salt, derived] = stored.split(':');
    const check = crypto.scryptSync(plain, salt, 64).toString('hex');
    return crypto.timingSafeEqual(Buffer.from(derived), Buffer.from(check));
}

module.exports = { hashPassword, verifyPassword };
