"""Composition root — monta a aplicação Flask (config, DB, rotas, error handlers)."""
import logging

from flask import Flask
from flask_cors import CORS

from src.config import settings
from src.config.database import init_db
from src.views.routes import register_routes
from src.middlewares.error_handler import register_error_handlers


def create_app():
    logging.basicConfig(level=logging.INFO)
    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["DEBUG"] = settings.DEBUG
    CORS(app)

    init_db()
    register_routes(app)
    register_error_handlers(app)
    return app


app = create_app()

if __name__ == "__main__":
    print("=" * 50)
    print("SERVIDOR INICIADO")
    print(f"Rodando em http://localhost:{settings.PORT}")
    print("=" * 50)
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
