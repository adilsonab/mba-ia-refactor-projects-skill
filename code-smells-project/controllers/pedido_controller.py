from flask import current_app, jsonify

from controllers.validators import require_json, validar_itens_pedido
from errors import ValidationError


def _service():
    return current_app.extensions["pedido_service"]


def criar_pedido():
    dados = require_json()
    usuario_id = dados.get("usuario_id")
    if not usuario_id:
        raise ValidationError("Usuario ID é obrigatório")
    itens = validar_itens_pedido(dados.get("itens", []))

    resultado = _service().criar(usuario_id, itens)
    return jsonify({"dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso"}), 201


def listar_pedidos_usuario(usuario_id):
    return jsonify({"dados": _service().listar(usuario_id), "sucesso": True}), 200


def listar_todos_pedidos():
    return jsonify({"dados": _service().listar(), "sucesso": True}), 200


def atualizar_status_pedido(pedido_id):
    dados = require_json()
    _service().atualizar_status(pedido_id, dados.get("status", ""))
    return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
