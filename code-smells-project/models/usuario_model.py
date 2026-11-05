"""Data access for the `usuarios` table. Passwords arrive here already hashed."""
from database import get_db

COLUNAS = "id, nome, email, senha, tipo, criado_em"


def listar():
    rows = get_db().execute(f"SELECT {COLUNAS} FROM usuarios").fetchall()
    return [dict(row) for row in rows]


def buscar_por_id(usuario_id):
    row = get_db().execute(f"SELECT {COLUNAS} FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
    return dict(row) if row else None


def buscar_por_email(email):
    rows = get_db().execute(f"SELECT {COLUNAS} FROM usuarios WHERE email = ? ORDER BY id", (email,)).fetchall()
    return [dict(row) for row in rows]


def criar(nome, email, senha_hash, tipo):
    conn = get_db()
    with conn:
        cursor = conn.execute(
            "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
            (nome, email, senha_hash, tipo),
        )
    return cursor.lastrowid
