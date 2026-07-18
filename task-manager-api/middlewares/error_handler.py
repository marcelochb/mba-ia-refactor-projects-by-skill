"""Tratamento de erro centralizado — sem vazar stack trace ao cliente."""
import logging

from flask import jsonify

from middlewares.validation import ValidationError

logger = logging.getLogger("taskmanager.error")


def register_error_handlers(app):
    @app.errorhandler(ValidationError)
    def handle_validation(err):
        return jsonify({"error": err.mensagem}), err.status

    @app.errorhandler(404)
    def handle_not_found(_err):
        return jsonify({"error": "Recurso não encontrado"}), 404

    @app.errorhandler(Exception)
    def handle_unexpected(err):
        logger.exception("Erro inesperado: %s", err)
        return jsonify({"error": "Erro interno"}), 500
