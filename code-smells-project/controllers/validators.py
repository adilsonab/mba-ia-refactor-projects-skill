"""Validação de entrada centralizada (mesmas mensagens do código original quando existiam)."""
from flask import request

from config.constants import CATEGORIA_PADRAO, CATEGORIAS_VALIDAS, NOME_PRODUTO_MAX, NOME_PRODUTO_MIN
from errors import ValidationError

DADOS_INVALIDOS = "Dados inválidos"


def json_body(permitir_vazio=False):
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict) or (not dados and not permitir_vazio):
        raise ValidationError(DADOS_INVALIDOS)
    return dados


def _is_number(valor):
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def _is_int(valor):
    return isinstance(valor, int) and not isinstance(valor, bool)


def produto_payload(dados):
    """Mesmas regras para criação e atualização."""
    for campo, mensagem in (("nome", "Nome é obrigatório"), ("preco", "Preço é obrigatório"),
                            ("estoque", "Estoque é obrigatório")):
        if campo not in dados:
            raise ValidationError(mensagem)

    nome = dados["nome"]
    descricao = dados.get("descricao", "")
    preco = dados["preco"]
    estoque = dados["estoque"]
    categoria = dados.get("categoria", CATEGORIA_PADRAO)

    if not _is_number(preco):
        raise ValidationError("Preço deve ser numérico")
    if not _is_int(estoque):
        raise ValidationError("Estoque deve ser um número inteiro")
    if not isinstance(nome, str):
        raise ValidationError("Nome deve ser texto")
    if descricao is None:
        descricao = ""
    if not isinstance(descricao, str):
        raise ValidationError("Descrição deve ser texto")

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

    return {"nome": nome, "descricao": descricao, "preco": preco, "estoque": estoque, "categoria": categoria}


def query_float(nome):
    valor = request.args.get(nome)
    if valor is None or valor == "":
        return None
    try:
        return float(valor)
    except ValueError:
        raise ValidationError(nome + " deve ser numérico") from None


def usuario_payload(dados):
    nome = dados.get("nome", "")
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    if not all(isinstance(v, str) for v in (nome, email, senha)) or not nome or not email or not senha:
        raise ValidationError("Nome, email e senha são obrigatórios")
    if "@" not in email:
        raise ValidationError("Email inválido")
    return nome, email, senha


def login_payload(dados):
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    if not isinstance(email, str) or not isinstance(senha, str) or not email or not senha:
        raise ValidationError("Email e senha são obrigatórios")
    return email, senha


def itens_pedido(dados):
    itens = dados.get("itens", [])
    if not itens:
        raise ValidationError("Pedido deve ter pelo menos 1 item")
    if not isinstance(itens, list):
        raise ValidationError("Itens inválidos")
    validos = []
    for item in itens:
        if not isinstance(item, dict):
            raise ValidationError("Item inválido: produto_id e quantidade (inteiro > 0) são obrigatórios")
        produto_id, quantidade = item.get("produto_id"), item.get("quantidade")
        if not _is_int(produto_id) or not _is_int(quantidade) or produto_id <= 0 or quantidade <= 0:
            raise ValidationError("Item inválido: produto_id e quantidade (inteiro > 0) são obrigatórios")
        validos.append({"produto_id": produto_id, "quantidade": quantidade})
    return validos


def usuario_id_opcional(dados):
    usuario_id = dados.get("usuario_id")
    if usuario_id is None:
        return None
    if not _is_int(usuario_id) or usuario_id <= 0:
        raise ValidationError("Usuario ID inválido")
    return usuario_id
