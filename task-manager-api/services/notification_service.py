"""Notificações por e-mail com dependências injetáveis.

O serviço é criado no composition root (``app.extensions['notifications']``), mas ainda não está
ligado a nenhuma rota: disparar notificações em eventos é decisão de negócio pendente.
"""
import logging
import smtplib

from utils.helpers import utc_now

logger = logging.getLogger(__name__)


class SmtpSender:
    def __init__(self, host, port, user, password):
        self.host, self.port, self.user, self.password = host, port, user, password

    @property
    def enabled(self):
        return bool(self.host and self.user and self.password)

    def send(self, to, subject, body):
        if not self.enabled:
            logger.warning('SMTP não configurado; e-mail para %s não enviado', to)
            return False
        message = f'Subject: {subject}\n\n{body}'
        with smtplib.SMTP(self.host, self.port) as server:
            server.starttls()
            server.login(self.user, self.password)
            server.sendmail(self.user, to, message)
        return True


class NotificationService:
    def __init__(self, sender, store=None):
        self.sender = sender
        # histórico injetável; o padrão é uma lista em memória (volátil: perde-se a cada boot)
        self.notifications = store if store is not None else []

    @classmethod
    def from_config(cls, config):
        sender = SmtpSender(config['SMTP_HOST'], config['SMTP_PORT'], config['SMTP_USER'], config['SMTP_PASSWORD'])
        return cls(sender)

    def send_email(self, to, subject, body):
        try:
            sent = self.sender.send(to, subject, body)
        except (smtplib.SMTPException, OSError):
            logger.exception('Erro ao enviar email para %s', to)
            return False
        if sent:
            logger.info('Email enviado para %s', to)
        return sent

    def notify_task_assigned(self, user, task):
        subject = f'Nova task atribuída: {task.title}'
        body = (f"Olá {user.name},\n\nA task '{task.title}' foi atribuída a você.\n\n"
                f'Prioridade: {task.priority}\nStatus: {task.status}')
        self.send_email(user.email, subject, body)
        self.notifications.append({
            'type': 'task_assigned',
            'user_id': user.id,
            'task_id': task.id,
            'timestamp': utc_now(),
        })

    def notify_task_overdue(self, user, task):
        subject = f'Task atrasada: {task.title}'
        body = f"Olá {user.name},\n\nA task '{task.title}' está atrasada!\n\nData limite: {task.due_date}"
        self.send_email(user.email, subject, body)

    def get_notifications(self, user_id):
        return [notification for notification in self.notifications if notification['user_id'] == user_id]
