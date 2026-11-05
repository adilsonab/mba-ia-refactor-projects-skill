"""Response presenters: explicit public fields per entity (no passwords or secrets)."""

PRODUTO_CAMPOS = ("id", "nome", "descricao", "preco", "estoque", "categoria", "ativo", "criado_em")
USUARIO_CAMPOS = ("id", "nome", "email", "tipo", "criado_em")
USUARIO_LOGIN_CAMPOS = ("id", "nome", "email", "tipo")


def _pick(registro, campos):
    return {campo: registro[campo] for campo in campos}


def produto(registro):
    return _pick(registro, PRODUTO_CAMPOS)


def produtos(registros):
    return [produto(r) for r in registros]


def usuario(registro):
    return _pick(registro, USUARIO_CAMPOS)


def usuarios(registros):
    return [usuario(r) for r in registros]


def usuario_login(registro):
    return _pick(registro, USUARIO_LOGIN_CAMPOS)
