"""Controller de Usuário — fino: valida, delega ao model, responde."""
from flask import request, jsonify
from src.models import usuario_model
from src.middlewares.validation import validar_usuario, validar_login


def listar():
    return jsonify({"dados": usuario_model.listar(), "sucesso": True}), 200


def buscar(id):
    usuario = usuario_model.buscar_por_id(id)
    if not usuario:
        return jsonify({"erro": "Usuário não encontrado"}), 404
    return jsonify({"dados": usuario, "sucesso": True}), 200


def criar():
    dados = validar_usuario(request.get_json())
    novo_id = usuario_model.criar(dados["nome"], dados["email"], dados["senha"])
    return jsonify({"dados": {"id": novo_id}, "sucesso": True}), 201


def login():
    dados = validar_login(request.get_json())
    usuario = usuario_model.autenticar(dados["email"], dados["senha"])
    if usuario:
        return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200
    return jsonify({"erro": "Email ou senha inválidos", "sucesso": False}), 401
