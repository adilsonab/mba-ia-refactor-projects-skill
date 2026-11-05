"""Notification channel (email/SMS/push). Current implementation only logs; swap it in app.create_app()."""
import logging


class NotificationService:
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger("notificacoes")

    def pedido_criado(self, pedido_id, usuario_id):
        self.logger.info("ENVIANDO EMAIL: Pedido %s criado para usuario %s", pedido_id, usuario_id)
        self.logger.info("ENVIANDO SMS: Seu pedido foi recebido!")
        self.logger.info("ENVIANDO PUSH: Novo pedido recebido pelo sistema")

    def pedido_aprovado(self, pedido_id):
        self.logger.info("NOTIFICAÇÃO: Pedido %s foi aprovado! Preparar envio.", pedido_id)

    def pedido_cancelado(self, pedido_id):
        self.logger.info("NOTIFICAÇÃO: Pedido %s cancelado. Devolver estoque.", pedido_id)
