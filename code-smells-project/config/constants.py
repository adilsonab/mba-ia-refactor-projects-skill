"""Constantes de negócio nomeadas (valores idênticos aos do código original)."""

API_VERSION = "1.0.0"

CATEGORIAS_VALIDAS = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]
CATEGORIA_PADRAO = "geral"
NOME_PRODUTO_MIN = 2
NOME_PRODUTO_MAX = 200

STATUS_PENDENTE = "pendente"
STATUS_APROVADO = "aprovado"
STATUS_CANCELADO = "cancelado"
STATUS_PEDIDO = [STATUS_PENDENTE, STATUS_APROVADO, "enviado", "entregue", STATUS_CANCELADO]
STATUS_INICIAL_PEDIDO = STATUS_PENDENTE
STATUS_NOTIFICADOS = (STATUS_APROVADO, STATUS_CANCELADO)  # mudanças que disparam notificação

# (faturamento mínimo exclusivo, taxa de desconto), da maior faixa para a menor
FAIXAS_DESCONTO = ((10000, 0.10), (5000, 0.05), (1000, 0.02))

TIPO_CLIENTE = "cliente"
TIPO_ADMIN = "admin"
