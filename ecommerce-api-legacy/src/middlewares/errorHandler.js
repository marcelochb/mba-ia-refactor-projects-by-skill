'use strict';

// Tratamento de erro centralizado — não expõe stack trace ao cliente.
// eslint-disable-next-line no-unused-vars
function errorHandler(err, req, res, next) {
    const status = err.status || 500;
    const message = err.status ? err.message : 'Erro interno do servidor';
    res.status(status).send(message);
}

module.exports = { errorHandler };
