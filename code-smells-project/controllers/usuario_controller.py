from flask import jsonify

from controllers import validators
from errors import UnauthorizedError
from middlewares.auth import ensure_self_or_admin
from services import auth_service, usuario_service


def listar_usuarios():
    return jsonify({"dados": usuario_service.listar(), "sucesso": True}), 200


def buscar_usuario(usuario_id):
    ensure_self_or_admin(usuario_id)
    return jsonify({"dados": usuario_service.obter(usuario_id), "sucesso": True}), 200


def criar_usuario():
    nome, email, senha = validators.usuario_payload(validators.json_body())
    usuario_id = usuario_service.cadastrar(nome, email, senha)  # tipo do corpo é ignorado
    return jsonify({"dados": {"id": usuario_id}, "sucesso": True}), 201


def login():
    email, senha = validators.login_payload(validators.json_body(permitir_vazio=True))
    usuario = usuario_service.autenticar(email, senha)
    if usuario is None:
        raise UnauthorizedError("Email ou senha inválidos")
    return jsonify({
        "dados": usuario,
        "sucesso": True,
        "mensagem": "Login OK",
        "token": auth_service.emitir_token(usuario),
    }), 200
