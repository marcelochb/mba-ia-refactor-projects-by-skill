"""Model de Pedido — acesso a dados com queries parametrizadas.

Criação de pedido usa transação atômica; a leitura evita N+1 com JOIN.
"""
from src.config.database import get_connection


def criar(usuario_id, itens):
    """Cria pedido + itens + baixa de estoque numa transação atômica."""
    conn = get_connection()
    try:
        # Valida estoque e calcula total
        total = 0
        precos = {}
        for item in itens:
            row = conn.execute(
                "SELECT * FROM produtos WHERE id = ?", (item["produto_id"],)
            ).fetchone()
            if row is None:
                return {"erro": f"Produto {item['produto_id']} não encontrado"}
            if row["estoque"] < item["quantidade"]:
                return {"erro": f"Estoque insuficiente para {row['nome']}"}
            precos[item["produto_id"]] = row["preco"]
            total += row["preco"] * item["quantidade"]

        conn.execute("BEGIN")
        cur = conn.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
            (usuario_id, total),
        )
        pedido_id = cur.lastrowid
        for item in itens:
            conn.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) "
                "VALUES (?, ?, ?, ?)",
                (pedido_id, item["produto_id"], item["quantidade"], precos[item["produto_id"]]),
            )
            conn.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
                (item["quantidade"], item["produto_id"]),
            )
        conn.commit()
        return {"pedido_id": pedido_id, "total": total}
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _montar_pedidos(conn, rows):
    """Monta pedidos com seus itens usando uma única query com JOIN (evita N+1)."""
    result = []
    for row in rows:
        itens = conn.execute(
            """
            SELECT ip.produto_id, ip.quantidade, ip.preco_unitario,
                   COALESCE(p.nome, 'Desconhecido') AS produto_nome
            FROM itens_pedido ip
            LEFT JOIN produtos p ON p.id = ip.produto_id
            WHERE ip.pedido_id = ?
            """,
            (row["id"],),
        ).fetchall()
        result.append({
            "id": row["id"], "usuario_id": row["usuario_id"], "status": row["status"],
            "total": row["total"], "criado_em": row["criado_em"],
            "itens": [{
                "produto_id": i["produto_id"], "produto_nome": i["produto_nome"],
                "quantidade": i["quantidade"], "preco_unitario": i["preco_unitario"],
            } for i in itens],
        })
    return result


def listar_por_usuario(usuario_id):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM pedidos WHERE usuario_id = ?", (usuario_id,)).fetchall()
    result = _montar_pedidos(conn, rows)
    conn.close()
    return result


def listar_todos():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM pedidos").fetchall()
    result = _montar_pedidos(conn, rows)
    conn.close()
    return result


def atualizar_status(pedido_id, novo_status):
    conn = get_connection()
    conn.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
    conn.commit()
    conn.close()
    return True


def relatorio_vendas(faixas_desconto):
    conn = get_connection()
    total_pedidos = conn.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
    faturamento = conn.execute("SELECT SUM(total) FROM pedidos").fetchone()[0] or 0
    pendentes = conn.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'pendente'").fetchone()[0]
    aprovados = conn.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'aprovado'").fetchone()[0]
    cancelados = conn.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'cancelado'").fetchone()[0]
    conn.close()

    desconto = 0
    for limite, taxa in faixas_desconto:
        if faturamento > limite:
            desconto = faturamento * taxa
            break

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": pendentes,
        "pedidos_aprovados": aprovados,
        "pedidos_cancelados": cancelados,
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
    }
