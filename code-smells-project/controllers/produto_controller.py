from flask import jsonify, request

from controllers import validators
from services import produto_service


def listar_produtos():
    return jsonify({"dados": produto_service.listar(), "sucesso": True}), 200


def buscar_produto(produto_id):
    return jsonify({"dados": produto_service.obter(produto_id), "sucesso": True}), 200


def criar_produto():
    campos = validators.produto_payload(validators.json_body())
    produto_id = produto_service.criar(campos)
    return jsonify({"dados": {"id": produto_id}, "sucesso": True, "mensagem": "Produto criado"}), 201


def atualizar_produto(produto_id):
    produto_service.garantir_existe(produto_id)  # 404 antes da validação, como no original
    campos = validators.produto_payload(validators.json_body())
    produto_service.atualizar(produto_id, campos)
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


def deletar_produto(produto_id):
    produto_service.deletar(produto_id)
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200


def buscar_produtos():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria") or None
    preco_min = validators.query_float("preco_min")
    preco_max = validators.query_float("preco_max")
    resultados = produto_service.buscar(termo, categoria, preco_min, preco_max)
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200
