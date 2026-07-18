"""Validação de input reutilizável (borda)."""
import re
from datetime import datetime

from config import settings

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$")


class ValidationError(Exception):
    def __init__(self, mensagem, status=400):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.status = status


def _parse_due_date(valor):
    try:
        return datetime.strptime(valor, "%Y-%m-%d")
    except (ValueError, TypeError):
        raise ValidationError("Formato de data inválido. Use YYYY-MM-DD")


def _normalizar_tags(tags):
    return ",".join(tags) if isinstance(tags, list) else tags


def _validar_titulo(titulo):
    if not titulo:
        raise ValidationError("Título é obrigatório")
    if len(titulo) < settings.MIN_TITLE_LENGTH:
        raise ValidationError("Título muito curto")
    if len(titulo) > settings.MAX_TITLE_LENGTH:
        raise ValidationError("Título muito longo")
    return titulo


def validar_task_criacao(dados):
    if not dados:
        raise ValidationError("Dados inválidos")
    campos = {"title": _validar_titulo(dados.get("title"))}
    campos["description"] = dados.get("description", "")

    status = dados.get("status", "pending")
    if status not in settings.VALID_STATUSES:
        raise ValidationError("Status inválido")
    campos["status"] = status

    priority = dados.get("priority", 3)
    if priority < 1 or priority > 5:
        raise ValidationError("Prioridade deve ser entre 1 e 5")
    campos["priority"] = priority

    campos["user_id"] = dados.get("user_id")
    campos["category_id"] = dados.get("category_id")
    if dados.get("due_date"):
        campos["due_date"] = _parse_due_date(dados["due_date"])
    if dados.get("tags"):
        campos["tags"] = _normalizar_tags(dados["tags"])
    return campos


def validar_task_atualizacao(dados):
    if not dados:
        raise ValidationError("Dados inválidos")
    campos = {}
    if "title" in dados:
        campos["title"] = _validar_titulo(dados["title"])
    if "description" in dados:
        campos["description"] = dados["description"]
    if "status" in dados:
        if dados["status"] not in settings.VALID_STATUSES:
            raise ValidationError("Status inválido")
        campos["status"] = dados["status"]
    if "priority" in dados:
        if dados["priority"] < 1 or dados["priority"] > 5:
            raise ValidationError("Prioridade deve ser entre 1 e 5")
        campos["priority"] = dados["priority"]
    if "user_id" in dados:
        campos["user_id"] = dados["user_id"]
    if "category_id" in dados:
        campos["category_id"] = dados["category_id"]
    if "due_date" in dados:
        campos["due_date"] = _parse_due_date(dados["due_date"]) if dados["due_date"] else None
    if "tags" in dados:
        campos["tags"] = _normalizar_tags(dados["tags"])
    return campos


def validar_usuario_criacao(dados):
    if not dados:
        raise ValidationError("Dados inválidos")
    name, email, password = dados.get("name"), dados.get("email"), dados.get("password")
    if not name:
        raise ValidationError("Nome é obrigatório")
    if not email:
        raise ValidationError("Email é obrigatório")
    if not password:
        raise ValidationError("Senha é obrigatória")
    if not _EMAIL_RE.match(email):
        raise ValidationError("Email inválido")
    if len(password) < settings.MIN_PASSWORD_LENGTH:
        raise ValidationError("Senha deve ter no mínimo 4 caracteres")
    role = dados.get("role", "user")
    if role not in settings.VALID_ROLES:
        raise ValidationError("Role inválido")
    return {"name": name, "email": email, "password": password, "role": role}


def validar_email(email):
    if not _EMAIL_RE.match(email):
        raise ValidationError("Email inválido")
    return email
