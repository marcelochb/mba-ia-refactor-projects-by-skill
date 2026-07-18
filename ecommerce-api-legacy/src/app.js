'use strict';

// Composition root — monta a aplicação (config, DB, rotas, error handler).
const express = require('express');
const config = require('./config');
const db = require('./config/database');
const routes = require('./routes');
const { errorHandler } = require('./middlewares/errorHandler');

async function bootstrap() {
    const app = express();
    app.use(express.json());

    await db.init();

    app.use('/api', routes);
    app.use(errorHandler);

    app.listen(config.port, () => {
        console.log(`LMS API rodando na porta ${config.port}...`);
    });

    return app;
}

bootstrap().catch((err) => {
    console.error('Falha ao iniciar a aplicação:', err.message);
    process.exit(1);
});
