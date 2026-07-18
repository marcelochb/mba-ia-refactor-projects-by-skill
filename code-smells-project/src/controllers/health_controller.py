"""Controller de health check — sem expor segredos/configuração sensível."""
from flask import jsonify
from src.config.database import get_connection


def health():
    conn = get_connection()
    counts = {
        "produtos": conn.execute("SELECT COUNT(*) FROM produtos").fetchone()[0],
        "usuarios": conn.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0],
        "pedidos": conn.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0],
    }
    conn.close()
    return jsonify({
        "status": "ok",
        "database": "connected",
        "counts": counts,
        "versao": "1.0.0",
    }), 200
