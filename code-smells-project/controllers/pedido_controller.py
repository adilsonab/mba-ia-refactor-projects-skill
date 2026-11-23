from flask import current_app, g, jsonify

from controllers import validators
from middlewares.auth import ensure_self_or_admin


def _service():
    return current_app.extensions["pedido_service"]


def criar_pedido():
    dados = validators.json_body()
    usuario_id = validators.usuario_id_opcional(dados) or g.current_user["id"]
    ensure_self_or_admin(usuario_id)
    itens = validators.itens_pedido(dados)
    resultado = _service().criar(usuario_id, itens)
    return jsonify({"dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso"}), 201


def listar_pedidos_usuario(usuario_id):
    ensure_self_or_admin(usuario_id)
    return jsonify({"dados": _service().listar_por_usuario(usuario_id), "sucesso": True}), 200


def listar_todos_pedidos():
    return jsonify({"dados": _service().listar_todos(), "sucesso": True}), 200


def atualizar_status_pedido(pedido_id):
    dados = validators.json_body(permitir_vazio=True)
    _service().atualizar_status(pedido_id, dados.get("status", ""))
    return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
