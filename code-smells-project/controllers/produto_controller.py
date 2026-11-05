import logging

from flask import jsonify, request

from controllers.validators import parse_preco_query, require_json, validar_produto
from errors import NotFoundError
from models import produto_model
from views import serializers

logger = logging.getLogger(__name__)


def _buscar_ou_404(produto_id, mensagem="Produto não encontrado"):
    produto = produto_model.buscar_por_id(produto_id)
    if not produto:
        raise NotFoundError(mensagem)
    return produto


def listar_produtos():
    produtos = produto_model.listar()
    logger.info("Listando %d produtos", len(produtos))
    return jsonify({"dados": serializers.produtos(produtos), "sucesso": True}), 200


def buscar_produto(produto_id):
    produto = _buscar_ou_404(produto_id)
    return jsonify({"dados": serializers.produto(produto), "sucesso": True}), 200


def criar_produto():
    nome, descricao, preco, estoque, categoria = validar_produto(require_json())
    produto_id = produto_model.criar(nome, descricao, preco, estoque, categoria)
    logger.info("Produto criado com ID: %s", produto_id)
    return jsonify({"dados": {"id": produto_id}, "sucesso": True, "mensagem": "Produto criado"}), 201


def atualizar_produto(produto_id):
    _buscar_ou_404(produto_id)
    nome, descricao, preco, estoque, categoria = validar_produto(require_json())
    produto_model.atualizar(produto_id, nome, descricao, preco, estoque, categoria)
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


def deletar_produto(produto_id):
    _buscar_ou_404(produto_id)
    produto_model.deletar(produto_id)
    logger.info("Produto %s deletado", produto_id)
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200


def buscar_produtos():
    resultados = produto_model.pesquisar(
        termo=request.args.get("q", ""),
        categoria=request.args.get("categoria"),
        preco_min=parse_preco_query("preco_min"),
        preco_max=parse_preco_query("preco_max"),
    )
    return jsonify({"dados": serializers.produtos(resultados), "total": len(resultados), "sucesso": True}), 200
