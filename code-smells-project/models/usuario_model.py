"""Acesso a dados de usuários. As leituras públicas nunca retornam a coluna senha."""
from database import get_db

_COLUNAS_PUBLICAS = "id, nome, email, tipo, criado_em"


def _to_dict(row):
    return dict(row) if row else None


def listar():
    rows = get_db().execute(f"SELECT {_COLUNAS_PUBLICAS} FROM usuarios ORDER BY id").fetchall()
    return [_to_dict(row) for row in rows]


def buscar_por_id(usuario_id):
    row = get_db().execute(
        f"SELECT {_COLUNAS_PUBLICAS} FROM usuarios WHERE id = ?", (usuario_id,)
    ).fetchone()
    return _to_dict(row)


def buscar_credenciais_por_email(email):
    """Uso interno (login): inclui o hash da senha."""
    row = get_db().execute(
        "SELECT id, nome, email, tipo, senha FROM usuarios WHERE email = ?", (email,)
    ).fetchone()
    return _to_dict(row)


def email_existe(email):
    return get_db().execute("SELECT 1 FROM usuarios WHERE email = ?", (email,)).fetchone() is not None


def criar(nome, email, senha_hash, tipo):
    cursor = get_db().execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, senha_hash, tipo),
    )
    return cursor.lastrowid
