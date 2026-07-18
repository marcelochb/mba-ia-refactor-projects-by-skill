"""Validação de input reutilizável (borda) — levanta ValidationError com status."""
from src.config import settings


class ValidationError(Exception):
    def __init__(self, mensagem, status=400):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.status = status


def validar_produto(dados):
    if not dados:
        raise ValidationError("Dados inválidos")
    for campo in ("nome", "preco", "estoque"):
        if campo not in dados:
            raise ValidationError(f"{campo} é obrigatório")
    nome = dados["nome"]
    if dados["preco"] < 0:
        raise ValidationError("Preço não pode ser negativo")
    if dados["estoque"] < 0:
        raise ValidationError("Estoque não pode ser negativo")
    if len(nome) < 2:
        raise ValidationError("Nome muito curto")
    if len(nome) > 200:
        raise ValidationError("Nome muito longo")
    categoria = dados.get("categoria", "geral")
    if categoria not in settings.CATEGORIAS_VALIDAS:
        raise ValidationError(f"Categoria inválida. Válidas: {settings.CATEGORIAS_VALIDAS}")
    return {
        "nome": nome,
        "descricao": dados.get("descricao", ""),
        "preco": dados["preco"],
        "estoque": dados["estoque"],
        "categoria": categoria,
    }


def validar_usuario(dados):
    if not dados:
        raise ValidationError("Dados inválidos")
    nome, email, senha = dados.get("nome", ""), dados.get("email", ""), dados.get("senha", "")
    if not nome or not email or not senha:
        raise ValidationError("Nome, email e senha são obrigatórios")
    return {"nome": nome, "email": email, "senha": senha}


def validar_login(dados):
    if not dados:
        raise ValidationError("Dados inválidos")
    email, senha = dados.get("email", ""), dados.get("senha", "")
    if not email or not senha:
        raise ValidationError("Email e senha são obrigatórios")
    return {"email": email, "senha": senha}


def validar_pedido(dados):
    if not dados:
        raise ValidationError("Dados inválidos")
    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])
    if not usuario_id:
        raise ValidationError("Usuario ID é obrigatório")
    if not itens:
        raise ValidationError("Pedido deve ter pelo menos 1 item")
    return {"usuario_id": usuario_id, "itens": itens}


def validar_status_pedido(dados):
    novo_status = (dados or {}).get("status", "")
    if novo_status not in settings.STATUS_PEDIDO_VALIDOS:
        raise ValidationError("Status inválido")
    return novo_status
