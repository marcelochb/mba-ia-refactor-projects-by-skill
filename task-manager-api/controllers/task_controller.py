"""Controller de Task — concentra o fluxo; usa models e validação."""
import logging
from datetime import datetime

from database import db
from models.task import Task
from models.user import User
from models.category import Category
from middlewares.validation import ValidationError, validar_task_criacao, validar_task_atualizacao

logger = logging.getLogger("taskmanager.task")


def _validar_relacionamentos(user_id, category_id):
    if user_id and not db.session.get(User, user_id):
        raise ValidationError("Usuário não encontrado", 404)
    if category_id and not db.session.get(Category, category_id):
        raise ValidationError("Categoria não encontrada", 404)


def listar():
    tasks = Task.query.all()
    return [t.to_dict(include_overdue=True, include_names=True) for t in tasks]


def obter(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        raise ValidationError("Task não encontrada", 404)
    return task.to_dict(include_overdue=True)


def criar(dados):
    campos = validar_task_criacao(dados)
    _validar_relacionamentos(campos.get("user_id"), campos.get("category_id"))

    task = Task()
    for chave, valor in campos.items():
        setattr(task, chave, valor)

    db.session.add(task)
    db.session.commit()
    logger.info("Task criada: %s - %s", task.id, task.title)
    return task.to_dict()


def atualizar(task_id, dados):
    task = db.session.get(Task, task_id)
    if not task:
        raise ValidationError("Task não encontrada", 404)

    campos = validar_task_atualizacao(dados)
    if "user_id" in campos or "category_id" in campos:
        _validar_relacionamentos(campos.get("user_id", task.user_id),
                                 campos.get("category_id", task.category_id))
    for chave, valor in campos.items():
        setattr(task, chave, valor)

    db.session.commit()
    logger.info("Task atualizada: %s", task.id)
    return task.to_dict()


def deletar(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        raise ValidationError("Task não encontrada", 404)
    db.session.delete(task)
    db.session.commit()
    logger.info("Task deletada: %s", task_id)


def buscar(query, status, priority, user_id):
    q = Task.query
    if query:
        q = q.filter(db.or_(Task.title.like(f"%{query}%"), Task.description.like(f"%{query}%")))
    if status:
        q = q.filter(Task.status == status)
    if priority:
        q = q.filter(Task.priority == int(priority))
    if user_id:
        q = q.filter(Task.user_id == int(user_id))
    return [t.to_dict() for t in q.all()]


def estatisticas():
    total = Task.query.count()
    counts = {
        s: Task.query.filter_by(status=s).count()
        for s in ("pending", "in_progress", "done", "cancelled")
    }
    overdue = sum(1 for t in Task.query.all() if t.is_overdue())
    done = counts["done"]
    return {
        "total": total,
        **counts,
        "overdue": overdue,
        "completion_rate": round((done / total) * 100, 2) if total > 0 else 0,
    }
