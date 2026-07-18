"""Model de Usuário — acesso a dados com queries parametrizadas.

A serialização pública NÃO inclui a senha (evita exposição de dado sensível).
"""
from src.config.database import get_connection


def _serialize(row):
    """Serialização pública — sem senha."""
    return {
        "id": row["id"], "nome": row["nome"], "email": row["email"],
        "tipo": row["tipo"], "criado_em": row["criado_em"],
    }


def listar():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM usuarios").fetchall()
    conn.close()
    return [_serialize(r) for r in rows]


def buscar_por_id(usuario_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
    conn.close()
    return _serialize(row) if row else None


def criar(nome, email, senha, tipo="cliente"):
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, senha, tipo),
    )
    conn.commit()
    novo_id = cur.lastrowid
    conn.close()
    return novo_id


def autenticar(email, senha):
    """Login com query parametrizada (não concatena input)."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM usuarios WHERE email = ? AND senha = ?", (email, senha)
    ).fetchone()
    conn.close()
    return _serialize(row) if row else None
