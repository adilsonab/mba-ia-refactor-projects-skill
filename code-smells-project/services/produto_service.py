"""Casos de uso de produtos."""
import logging

from errors import NotFoundError
from models import produto_model

logger = logging.getLogger(__name__)

PRODUTO_NAO_ENCONTRADO = "Produto não encontrado"


def listar():
    produtos = produto_model.listar()
    logger.info("Listando %d produtos", len(produtos))
    return produtos


def obter(produto_id):
    produto = produto_model.buscar_por_id(produto_id)
    if produto is None:
        raise NotFoundError(PRODUTO_NAO_ENCONTRADO)
    return produto


def criar(campos):
    produto_id = produto_model.criar(**campos)
    logger.info("Produto criado com ID %s", produto_id)
    return produto_id


def garantir_existe(produto_id):
    obter(produto_id)


def atualizar(produto_id, campos):
    if not produto_model.atualizar(produto_id, **campos):
        raise NotFoundError(PRODUTO_NAO_ENCONTRADO)


def deletar(produto_id):
    if not produto_model.desativar(produto_id):
        raise NotFoundError(PRODUTO_NAO_ENCONTRADO)
    logger.info("Produto %s desativado", produto_id)


def buscar(termo, categoria, preco_min, preco_max):
    return produto_model.buscar(termo, categoria, preco_min, preco_max)
