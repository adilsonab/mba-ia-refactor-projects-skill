"""Data access for the `produtos` table (parameterized queries only).

Deletion is a soft delete (`ativo = 0`): order history keeps pointing to the product (AP-20),
while every catalog read only sees active products.
"""
from database import get_db

COLUNAS = "id, nome, descricao, preco, estoque, categoria, ativo, criado_em"


def listar():
    rows = get_db().execute(f"SELECT {COLUNAS} FROM produtos WHERE ativo = 1").fetchall()
    return [dict(row) for row in rows]


def buscar_por_id(produto_id):
    row = get_db().execute(f"SELECT {COLUNAS} FROM produtos WHERE id = ? AND ativo = 1", (produto_id,)).fetchone()
    return dict(row) if row else None


def buscar_por_ids(produto_ids):
    """Returns {id: produto} for the given ids in a single query."""
    ids = list(set(produto_ids))
    if not ids:
        return {}
    placeholders = ", ".join("?" for _ in ids)
    rows = get_db().execute(f"SELECT {COLUNAS} FROM produtos WHERE ativo = 1 AND id IN ({placeholders})", ids).fetchall()
    return {row["id"]: dict(row) for row in rows}


def pesquisar(termo=None, categoria=None, preco_min=None, preco_max=None):
    clausulas, params = ["ativo = 1"], []
    if termo:
        clausulas.append("(nome LIKE ? OR descricao LIKE ?)")
        params += [f"%{termo}%", f"%{termo}%"]
    if categoria:
        clausulas.append("categoria = ?")
        params.append(categoria)
    if preco_min:
        clausulas.append("preco >= ?")
        params.append(preco_min)
    if preco_max:
        clausulas.append("preco <= ?")
        params.append(preco_max)
    # Only fixed clause strings are interpolated; every value goes through `params`.
    rows = get_db().execute(f"SELECT {COLUNAS} FROM produtos WHERE {' AND '.join(clausulas)}", params).fetchall()
    return [dict(row) for row in rows]


def criar(nome, descricao, preco, estoque, categoria):
    conn = get_db()
    with conn:
        cursor = conn.execute(
            "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
            (nome, descricao, preco, estoque, categoria),
        )
    return cursor.lastrowid


def atualizar(produto_id, nome, descricao, preco, estoque, categoria):
    conn = get_db()
    with conn:
        conn.execute(
            "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
            (nome, descricao, preco, estoque, categoria, produto_id),
        )


def deletar(produto_id):
    conn = get_db()
    with conn:
        conn.execute("UPDATE produtos SET ativo = 0 WHERE id = ?", (produto_id,))
