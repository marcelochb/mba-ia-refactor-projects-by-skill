"""Service de notificação — orquestração de efeitos colaterais fora do controller.

Neste projeto de exemplo as notificações são apenas registradas via logging
(não há integração real de email/SMS/push).
"""
import logging

logger = logging.getLogger("loja.notificacao")


def notificar_pedido_criado(pedido_id, usuario_id):
    logger.info("Pedido %s criado para usuário %s", pedido_id, usuario_id)


def notificar_status_pedido(pedido_id, status):
    if status == "aprovado":
        logger.info("Pedido %s aprovado — preparar envio", pedido_id)
    elif status == "cancelado":
        logger.info("Pedido %s cancelado — devolver estoque", pedido_id)
