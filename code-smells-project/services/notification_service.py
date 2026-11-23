"""Notificações (e-mail/SMS/push). Implementação padrão registra em log; troque por um canal real injetando outra classe."""
import logging


class NotificationService:
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)

    def notificar_pedido_criado(self, pedido_id, usuario_id):
        self.logger.info("Notificação (email/sms/push): pedido %s criado para usuário %s", pedido_id, usuario_id)

    def notificar_status_pedido(self, pedido_id, novo_status):
        self.logger.info("Notificação: pedido %s mudou para '%s'", pedido_id, novo_status)
