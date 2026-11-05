import logging

from flask import jsonify

from controllers.validators import require_json, texto_obrigatorio
from errors import NotFoundError, UnauthorizedError, ValidationError
from models import usuario_model
from services import usuario_service
from views import serializers

logger = logging.getLogger(__name__)


def listar_usuarios():
    return jsonify({"dados": serializers.usuarios(usuario_model.listar()), "sucesso": True}), 200


def buscar_usuario(usuario_id):
    usuario = usuario_model.buscar_por_id(usuario_id)
    if not usuario:
        raise NotFoundError("Usuário não encontrado")
    return jsonify({"dados": serializers.usuario(usuario), "sucesso": True}), 200


def criar_usuario():
    dados = require_json()
    nome = texto_obrigatorio(dados, "nome")
    email = texto_obrigatorio(dados, "email")
    senha = texto_obrigatorio(dados, "senha")
    if not nome or not email or not senha:
        raise ValidationError("Nome, email e senha são obrigatórios")

    usuario_id = usuario_service.criar(nome, email, senha)
    logger.info("Usuário criado: id=%s", usuario_id)
    return jsonify({"dados": {"id": usuario_id}, "sucesso": True}), 201


def login():
    dados = require_json()
    email = texto_obrigatorio(dados, "email")
    senha = texto_obrigatorio(dados, "senha")
    if not email or not senha:
        raise ValidationError("Email e senha são obrigatórios")

    usuario = usuario_service.autenticar(email, senha)
    if not usuario:
        logger.info("Falha de login")
        raise UnauthorizedError("Email ou senha inválidos")

    logger.info("Login bem-sucedido: usuario id=%s", usuario["id"])
    return jsonify({"dados": serializers.usuario_login(usuario), "sucesso": True, "mensagem": "Login OK"}), 200
