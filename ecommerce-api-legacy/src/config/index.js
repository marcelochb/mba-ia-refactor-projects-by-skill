'use strict';

// Configuração lida de variáveis de ambiente (sem segredos hardcoded).
module.exports = {
    port: process.env.PORT || 3000,
    dbFile: process.env.DB_FILE || ':memory:',
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
    smtpUser: process.env.SMTP_USER || '',
};
