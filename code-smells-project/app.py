"""Entry point na raiz — delega para a composition root em src/app.py.

Uso: `python app.py` (mantém compatibilidade com a forma original de iniciar).
"""
from src.app import app
from src.config import settings

if __name__ == "__main__":
    print("=" * 50)
    print("SERVIDOR INICIADO")
    print(f"Rodando em http://localhost:{settings.PORT}")
    print("=" * 50)
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
