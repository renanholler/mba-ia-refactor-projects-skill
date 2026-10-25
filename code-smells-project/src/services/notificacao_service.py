from flask import current_app


def notificar_pedido_criado(pedido_id, usuario_id):
    log = current_app.logger
    log.info("ENVIANDO EMAIL: Pedido %s criado para usuario %s", pedido_id, usuario_id)
    log.info("ENVIANDO SMS: Seu pedido foi recebido!")
    log.info("ENVIANDO PUSH: Novo pedido recebido pelo sistema")


def notificar_status(pedido_id, novo_status):
    log = current_app.logger
    if novo_status == "aprovado":
        log.info("NOTIFICAÇÃO: Pedido %s foi aprovado! Preparar envio.", pedido_id)
    if novo_status == "cancelado":
        log.info("NOTIFICAÇÃO: Pedido %s cancelado. Devolver estoque.", pedido_id)
