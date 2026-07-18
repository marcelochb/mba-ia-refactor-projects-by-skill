"""Controller de User — fluxo de usuários e login."""
import logging

from database import db
from models.user import User
from models.task import Task
from middlewares.validation import (
    ValidationError, validar_usuario_criacao, validar_email,
)
from config import settings

logger = logging.getLogger("taskmanager.user")


def listar():
    users = User.query.all()
    result = []
    for u in users:
        data = u.to_dict()
        data["task_count"] = len(u.tasks)
        result.append(data)
    return result


def obter(user_id):
    user = db.session.get(User, user_id)
    if not user:
        raise ValidationError("Usuário não encontrado", 404)
    data = user.to_dict()
    data["tasks"] = [t.to_dict() for t in user.tasks]
    return data


def criar(dados):
    campos = validar_usuario_criacao(dados)
    if User.query.filter_by(email=campos["email"]).first():
        raise ValidationError("Email já cadastrado", 409)

    user = User()
    user.name = campos["name"]
    user.email = campos["email"]
    user.set_password(campos["password"])
    user.role = campos["role"]
    db.session.add(user)
    db.session.commit()
    logger.info("Usuário criado: %s - %s", user.id, user.name)
    return user.to_dict()


def atualizar(user_id, dados):
    user = db.session.get(User, user_id)
    if not user:
        raise ValidationError("Usuário não encontrado", 404)
    if not dados:
        raise ValidationError("Dados inválidos")

    if "name" in dados:
        user.name = dados["name"]
    if "email" in dados:
        email = validar_email(dados["email"])
        existente = User.query.filter_by(email=email).first()
        if existente and existente.id != user_id:
            raise ValidationError("Email já cadastrado", 409)
        user.email = email
    if "password" in dados:
        if len(dados["password"]) < settings.MIN_PASSWORD_LENGTH:
            raise ValidationError("Senha muito curta")
        user.set_password(dados["password"])
    if "role" in dados:
        if dados["role"] not in settings.VALID_ROLES:
            raise ValidationError("Role inválido")
        user.role = dados["role"]
    if "active" in dados:
        user.active = dados["active"]

    db.session.commit()
    return user.to_dict()


def deletar(user_id):
    user = db.session.get(User, user_id)
    if not user:
        raise ValidationError("Usuário não encontrado", 404)
    for t in Task.query.filter_by(user_id=user_id).all():
        db.session.delete(t)
    db.session.delete(user)
    db.session.commit()
    logger.info("Usuário deletado: %s", user_id)


def listar_tasks(user_id):
    user = db.session.get(User, user_id)
    if not user:
        raise ValidationError("Usuário não encontrado", 404)
    return [t.to_dict(include_overdue=True) for t in user.tasks]


def login(dados):
    if not dados:
        raise ValidationError("Dados inválidos")
    email, password = dados.get("email"), dados.get("password")
    if not email or not password:
        raise ValidationError("Email e senha são obrigatórios")

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        raise ValidationError("Credenciais inválidas", 401)
    if not user.active:
        raise ValidationError("Usuário inativo", 403)

    # Retorna apenas dados públicos (to_dict não expõe senha).
    return {
        "message": "Login realizado com sucesso",
        "user": user.to_dict(),
        "token": f"session-{user.id}",
    }
