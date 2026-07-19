"""Configuração da aplicação — lida de variáveis de ambiente (sem segredos hardcoded)."""
import os

from dotenv import load_dotenv

# Carrega o .env para os.environ. Vars já definidas no ambiente têm prioridade
# (override=False), permitindo sobrescrever a config em produção/CI sem tocar no arquivo.
load_dotenv(override=False)

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
DB_PATH = os.environ.get("DB_PATH", "loja.db")
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "5000"))

# Regras de negócio parametrizadas (antes eram magic numbers no relatório de vendas)
FAIXAS_DESCONTO = [
    (10000, 0.10),
    (5000, 0.05),
    (1000, 0.02),
]

CATEGORIAS_VALIDAS = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]
STATUS_PEDIDO_VALIDOS = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]
