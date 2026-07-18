"""Tratamento de erro centralizado — sem vazar stack trace ao cliente."""
from flask import jsonify
from src.middlewares.validation import ValidationError


def register_error_handlers(app):
    @app.errorhandler(ValidationError)
    def handle_validation(err):
        return jsonify({"erro": err.mensagem, "sucesso": False}), err.status

    @app.errorhandler(404)
    def handle_not_found(_err):
        return jsonify({"erro": "Recurso não encontrado", "sucesso": False}), 404

    @app.errorhandler(Exception)
    def handle_unexpected(_err):
        # Não expõe detalhes internos ao cliente.
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500
