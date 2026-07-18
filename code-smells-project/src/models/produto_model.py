"""Model de Produto — acesso a dados com queries parametrizadas."""
from src.config.database import get_connection


def _serialize(row):
    return {
        "id": row["id"], "nome": row["nome"], "descricao": row["descricao"],
        "preco": row["preco"], "estoque": row["estoque"], "categoria": row["categoria"],
        "ativo": row["ativo"], "criado_em": row["criado_em"],
    }


def listar():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM produtos").fetchall()
    conn.close()
    return [_serialize(r) for r in rows]


def buscar_por_id(produto_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()
    conn.close()
    return _serialize(row) if row else None


def criar(nome, descricao, preco, estoque, categoria):
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        (nome, descricao, preco, estoque, categoria),
    )
    conn.commit()
    novo_id = cur.lastrowid
    conn.close()
    return novo_id


def atualizar(produto_id, nome, descricao, preco, estoque, categoria):
    conn = get_connection()
    conn.execute(
        "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
        (nome, descricao, preco, estoque, categoria, produto_id),
    )
    conn.commit()
    conn.close()
    return True


def deletar(produto_id):
    conn = get_connection()
    conn.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
    conn.commit()
    conn.close()
    return True


def buscar(termo=None, categoria=None, preco_min=None, preco_max=None):
    query = "SELECT * FROM produtos WHERE 1=1"
    params = []
    if termo:
        query += " AND (nome LIKE ? OR descricao LIKE ?)"
        params.extend([f"%{termo}%", f"%{termo}%"])
    if categoria:
        query += " AND categoria = ?"
        params.append(categoria)
    if preco_min is not None:
        query += " AND preco >= ?"
        params.append(preco_min)
    if preco_max is not None:
        query += " AND preco <= ?"
        params.append(preco_max)

    conn = get_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [_serialize(r) for r in rows]
