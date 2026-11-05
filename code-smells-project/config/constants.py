"""Named business constants (values preserved from the original code)."""

API_VERSION = "1.0.0"

# Products
CATEGORIAS_VALIDAS = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]
CATEGORIA_PADRAO = "geral"
NOME_PRODUTO_MIN = 2
NOME_PRODUTO_MAX = 200

# Users
TIPO_USUARIO_PADRAO = "cliente"

# Orders
STATUS_PEDIDO_INICIAL = "pendente"
STATUS_PEDIDO_APROVADO = "aprovado"
STATUS_PEDIDO_CANCELADO = "cancelado"
STATUS_PEDIDO_VALIDOS = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]
PRODUTO_DESCONHECIDO = "Desconhecido"

# Sales report: (exclusive minimum revenue, discount rate), checked in order
FAIXAS_DESCONTO = ((10000, 0.10), (5000, 0.05), (1000, 0.02))
