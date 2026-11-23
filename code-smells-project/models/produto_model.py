"""Acesso a dados de produtos. Exclusão é lógica (ativo = 0) para preservar o histórico de pedidos."""
from database import get_db

_COLUNAS = "id, nome, descricao, preco, estoque, categoria, ativo, criado_em"


def _to_dict(row):
    return dict(row) if row else None


def listar():
    rows = get_db().execute(f"SELECT {_COLUNAS} FROM produtos WHERE ativo = 1 ORDER BY id").fetchall()
    return [_to_dict(row) for row in rows]


def buscar_por_id(produto_id):
    row = get_db().execute(
        f"SELECT {_COLUNAS} FROM produtos WHERE id = ? AND ativo = 1", (produto_id,)
    ).fetchone()
    return _to_dict(row)


def buscar_por_ids(produto_ids):
    """Produtos ativos indexados por id (uma única query)."""
    ids = list(set(produto_ids))
    if not ids:
        return {}
    placeholders = ", ".join("?" for _ in ids)
    rows = get_db().execute(
        f"SELECT {_COLUNAS} FROM produtos WHERE ativo = 1 AND id IN ({placeholders})", ids
    ).fetchall()
    return {row["id"]: _to_dict(row) for row in rows}


def criar(nome, descricao, preco, estoque, categoria):
    cursor = get_db().execute(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        (nome, descricao, preco, estoque, categoria),
    )
    return cursor.lastrowid


def atualizar(produto_id, nome, descricao, preco, estoque, categoria):
    cursor = get_db().execute(
        "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? "
        "WHERE id = ? AND ativo = 1",
        (nome, descricao, preco, estoque, categoria, produto_id),
    )
    return cursor.rowcount > 0


def desativar(produto_id):
    cursor = get_db().execute("UPDATE produtos SET ativo = 0 WHERE id = ? AND ativo = 1", (produto_id,))
    return cursor.rowcount > 0


def buscar(termo, categoria=None, preco_min=None, preco_max=None):
    clausulas, params = ["ativo = 1"], []
    if termo:
        clausulas.append("(nome LIKE ? OR descricao LIKE ?)")
        params += [f"%{termo}%", f"%{termo}%"]
    if categoria:
        clausulas.append("categoria = ?")
        params.append(categoria)
    if preco_min is not None:
        clausulas.append("preco >= ?")
        params.append(preco_min)
    if preco_max is not None:
        clausulas.append("preco <= ?")
        params.append(preco_max)
    # Apenas cláusulas fixas são interpoladas; valores vão como parâmetros.
    sql = f"SELECT {_COLUNAS} FROM produtos WHERE {' AND '.join(clausulas)} ORDER BY id"
    return [_to_dict(row) for row in get_db().execute(sql, params).fetchall()]


def debitar_estoque(conn, produto_id, quantidade):
    """Débito atômico: só debita se houver estoque suficiente. Retorna False caso contrário."""
    cursor = conn.execute(
        "UPDATE produtos SET estoque = estoque - ? WHERE id = ? AND ativo = 1 AND estoque >= ?",
        (quantidade, produto_id, quantidade),
    )
    return cursor.rowcount > 0
