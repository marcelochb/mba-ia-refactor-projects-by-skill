'use strict';

const config = require('../config');

const STATUS_PAID = 'PAID';
const STATUS_DENIED = 'DENIED';

// Simulação de gateway. NÃO loga número de cartão nem a chave do gateway.
function authorize(card) {
    const approved = typeof card === 'string' && card.startsWith('4');
    // A chave do gateway seria usada aqui internamente; nunca é logada.
    void config.paymentGatewayKey;
    return approved ? STATUS_PAID : STATUS_DENIED;
}

module.exports = { authorize, STATUS_PAID, STATUS_DENIED };
