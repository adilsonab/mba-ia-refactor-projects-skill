"""Input validation shared by controllers. Original messages are preserved where they existed."""
from flask import request

from config.constants import CATEGORIA_PADRAO, CATEGORIAS_VALIDAS, NOME_PRODUTO_MAX, NOME_PRODUTO_MIN
from errors import ValidationError


def _is_int(valor):
    return isinstance(valor, int) and not isinstance(valor, bool)


def _is_number(valor):
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def require_json():
    dados = request.get_json(silent=True)
    if not dados or not isinstance(dados, dict):
        raise ValidationError("Dados inválidos")
    return dados


def validar_produto(dados):
    """Same rules for create and update. Returns (nome, descricao, preco, estoque, categoria)."""
    for campo, mensagem in (("nome", "Nome é obrigatório"), ("preco", "Preço é obrigatório"),
                            ("estoque", "Estoque é obrigatório")):
        if campo not in dados:
            raise ValidationError(mensagem)

    nome = dados["nome"]
    descricao = dados.get("descricao", "")
    preco = dados["preco"]
    estoque = dados["estoque"]
    categoria = dados.get("categoria", CATEGORIA_PADRAO)

    if not isinstance(nome, str):
        raise ValidationError("Nome inválido")
    if descricao is not None and not isinstance(descricao, str):
        raise ValidationError("Descrição inválida")
    if not _is_number(preco):
        raise ValidationError("Preço inválido")
    if not _is_int(estoque):
        raise ValidationError("Estoque inválido")

    if preco < 0:
        raise ValidationError("Preço não pode ser negativo")
    if estoque < 0:
        raise ValidationError("Estoque não pode ser negativo")
    if len(nome) < NOME_PRODUTO_MIN:
        raise ValidationError("Nome muito curto")
    if len(nome) > NOME_PRODUTO_MAX:
        raise ValidationError("Nome muito longo")
    if categoria not in CATEGORIAS_VALIDAS:
        raise ValidationError("Categoria inválida. Válidas: " + str(CATEGORIAS_VALIDAS))

    return nome, descricao, preco, estoque, categoria


def parse_preco_query(nome_param):
    valor = request.args.get(nome_param)
    if not valor:
        return None
    try:
        return float(valor)
    except ValueError:
        raise ValidationError(f"Parâmetro {nome_param} inválido") from None


def validar_itens_pedido(itens):
    if not itens:
        raise ValidationError("Pedido deve ter pelo menos 1 item")
    if not isinstance(itens, list):
        raise ValidationError("Itens inválidos")
    for item in itens:
        if (not isinstance(item, dict) or not _is_int(item.get("produto_id"))
                or not _is_int(item.get("quantidade")) or item["quantidade"] <= 0):
            raise ValidationError("Item inválido: produto_id e quantidade (inteiro maior que zero) são obrigatórios")
    return itens


def texto_obrigatorio(dados, campo):
    valor = dados.get(campo, "")
    return valor if isinstance(valor, str) else ""
