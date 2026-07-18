"""Controller de Produto — fino: valida, delega ao model, responde."""
from flask import request, jsonify
from src.models import produto_model
from src.middlewares.validation import validar_produto, ValidationError


def listar():
    return jsonify({"dados": produto_model.listar(), "sucesso": True}), 200


def buscar(id):
    produto = produto_model.buscar_por_id(id)
    if not produto:
        return jsonify({"erro": "Produto não encontrado", "sucesso": False}), 404
    return jsonify({"dados": produto, "sucesso": True}), 200


def criar():
    dados = validar_produto(request.get_json())
    novo_id = produto_model.criar(**dados)
    return jsonify({"dados": {"id": novo_id}, "sucesso": True, "mensagem": "Produto criado"}), 201


def atualizar(id):
    if not produto_model.buscar_por_id(id):
        return jsonify({"erro": "Produto não encontrado"}), 404
    dados = validar_produto(request.get_json())
    produto_model.atualizar(id, **dados)
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


def deletar(id):
    if not produto_model.buscar_por_id(id):
        return jsonify({"erro": "Produto não encontrado"}), 404
    produto_model.deletar(id)
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200


def buscar_produtos():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria", None)
    preco_min = request.args.get("preco_min", None)
    preco_max = request.args.get("preco_max", None)
    if preco_min:
        preco_min = float(preco_min)
    if preco_max:
        preco_max = float(preco_max)
    resultados = produto_model.buscar(termo, categoria, preco_min, preco_max)
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200
