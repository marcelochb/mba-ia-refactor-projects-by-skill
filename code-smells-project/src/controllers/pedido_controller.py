"""Controller de Pedido — fino: valida, delega ao model/service, responde."""
from flask import request, jsonify
from src.models import pedido_model
from src.services import notificacao_service
from src.middlewares.validation import validar_pedido, validar_status_pedido
from src.config import settings


def criar():
    dados = validar_pedido(request.get_json())
    resultado = pedido_model.criar(dados["usuario_id"], dados["itens"])
    if "erro" in resultado:
        return jsonify({"erro": resultado["erro"], "sucesso": False}), 400
    notificacao_service.notificar_pedido_criado(resultado["pedido_id"], dados["usuario_id"])
    return jsonify({"dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso"}), 201


def listar_por_usuario(usuario_id):
    return jsonify({"dados": pedido_model.listar_por_usuario(usuario_id), "sucesso": True}), 200


def listar_todos():
    return jsonify({"dados": pedido_model.listar_todos(), "sucesso": True}), 200


def atualizar_status(pedido_id):
    novo_status = validar_status_pedido(request.get_json())
    pedido_model.atualizar_status(pedido_id, novo_status)
    notificacao_service.notificar_status_pedido(pedido_id, novo_status)
    return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200


def relatorio_vendas():
    relatorio = pedido_model.relatorio_vendas(settings.FAIXAS_DESCONTO)
    return jsonify({"dados": relatorio, "sucesso": True}), 200
