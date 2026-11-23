"""Casos de uso de usuários: cadastro (papel definido pelo servidor) e autenticação."""
import logging

from config.constants import TIPO_CLIENTE
from errors import NotFoundError, ValidationError
from models import usuario_model
from models.passwords import hash_password, verify_password

logger = logging.getLogger(__name__)


def listar():
    return usuario_model.listar()


def obter(usuario_id):
    usuario = usuario_model.buscar_por_id(usuario_id)
    if usuario is None:
        raise NotFoundError("Usuário não encontrado")
    return usuario


def cadastrar(nome, email, senha):
    """Cadastro público: o papel é sempre o padrão (cliente), nunca vindo do cliente."""
    if usuario_model.email_existe(email):
        raise ValidationError("Email já cadastrado")
    usuario_id = usuario_model.criar(nome, email, hash_password(senha), TIPO_CLIENTE)
    logger.info("Usuário criado: id=%s", usuario_id)
    return usuario_id


def autenticar(email, senha):
    """Retorna o usuário público (id, nome, email, tipo) ou None."""
    registro = usuario_model.buscar_credenciais_por_email(email)
    if registro is None or not verify_password(registro["senha"], senha):
        logger.info("Falha de login")
        return None
    logger.info("Login bem-sucedido: id=%s", registro["id"])
    return {chave: registro[chave] for chave in ("id", "nome", "email", "tipo")}
