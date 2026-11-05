"""Notificações com transporte injetável (SMTP configurado por ambiente ou log em desenvolvimento)."""
import logging
import smtplib
from email.message import EmailMessage

logger = logging.getLogger(__name__)


class LogEmailTransport:
    """Transporte padrão de desenvolvimento: apenas registra o e-mail no log."""

    def send(self, to, subject, body):
        logger.info("E-mail (simulado) para %s: %s", to, subject)


class SmtpEmailTransport:
    def __init__(self, host, port, user, password, sender):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.sender = sender or user

    def send(self, to, subject, body):
        message = EmailMessage()
        message["From"] = self.sender
        message["To"] = to
        message["Subject"] = subject
        message.set_content(body)
        with smtplib.SMTP(self.host, self.port, timeout=10) as server:
            server.starttls()
            server.login(self.user, self.password)
            server.send_message(message)


class NotificationService:
    def __init__(self, transport):
        self.transport = transport

    def _send(self, to, subject, body):
        try:
            self.transport.send(to, subject, body)
            return True
        except (smtplib.SMTPException, OSError):
            logger.exception("Falha ao enviar e-mail para %s", to)
            return False

    def notify_task_assigned(self, user, task):
        subject = f"Nova task atribuída: {task.title}"
        body = (
            f"Olá {user.name},\n\nA task '{task.title}' foi atribuída a você.\n\n"
            f"Prioridade: {task.priority}\nStatus: {task.status}"
        )
        return self._send(user.email, subject, body)

    def notify_task_overdue(self, user, task):
        subject = f"Task atrasada: {task.title}"
        body = f"Olá {user.name},\n\nA task '{task.title}' está atrasada!\n\nData limite: {task.due_date}"
        return self._send(user.email, subject, body)


def build_notification_service(config):
    if config.get("SMTP_HOST") and config.get("SMTP_USER"):
        transport = SmtpEmailTransport(
            config["SMTP_HOST"], config["SMTP_PORT"], config["SMTP_USER"],
            config["SMTP_PASSWORD"], config.get("SMTP_SENDER"),
        )
    else:
        transport = LogEmailTransport()
    return NotificationService(transport)
