"""Controller de relatórios e categorias."""
from datetime import datetime, timezone, timedelta

from database import db
from models.task import Task
from models.user import User
from models.category import Category
from middlewares.validation import ValidationError


def _utcnow():
    return datetime.now(timezone.utc)


def resumo():
    total_tasks = Task.query.count()
    all_tasks = Task.query.all()

    por_status = {
        s: Task.query.filter_by(status=s).count()
        for s in ("pending", "in_progress", "done", "cancelled")
    }
    por_prioridade = {p: Task.query.filter_by(priority=p).count() for p in range(1, 6)}

    overdue_list = [
        {
            "id": t.id, "title": t.title, "due_date": str(t.due_date),
            "days_overdue": (_utcnow() - t.due_date.replace(tzinfo=timezone.utc)).days,
        }
        for t in all_tasks if t.is_overdue()
    ]

    sete_dias = _utcnow() - timedelta(days=7)
    recent_created = Task.query.filter(Task.created_at >= sete_dias).count()
    recent_done = Task.query.filter(Task.status == "done", Task.updated_at >= sete_dias).count()

    user_stats = []
    for u in User.query.all():
        tasks = u.tasks
        total = len(tasks)
        done = sum(1 for t in tasks if t.status == "done")
        user_stats.append({
            "user_id": u.id, "user_name": u.name,
            "total_tasks": total, "completed_tasks": done,
            "completion_rate": round((done / total) * 100, 2) if total > 0 else 0,
        })

    return {
        "generated_at": str(_utcnow()),
        "overview": {
            "total_tasks": total_tasks,
            "total_users": User.query.count(),
            "total_categories": Category.query.count(),
        },
        "tasks_by_status": por_status,
        "tasks_by_priority": {
            "critical": por_prioridade[1], "high": por_prioridade[2],
            "medium": por_prioridade[3], "low": por_prioridade[4], "minimal": por_prioridade[5],
        },
        "overdue": {"count": len(overdue_list), "tasks": overdue_list},
        "recent_activity": {
            "tasks_created_last_7_days": recent_created,
            "tasks_completed_last_7_days": recent_done,
        },
        "user_productivity": user_stats,
    }


def por_usuario(user_id):
    user = db.session.get(User, user_id)
    if not user:
        raise ValidationError("Usuário não encontrado", 404)
    tasks = user.tasks
    total = len(tasks)
    contagem = {s: 0 for s in ("done", "pending", "in_progress", "cancelled")}
    high_priority = 0
    overdue = 0
    for t in tasks:
        if t.status in contagem:
            contagem[t.status] += 1
        if t.priority <= 2:
            high_priority += 1
        if t.is_overdue():
            overdue += 1
    return {
        "user": {"id": user.id, "name": user.name, "email": user.email},
        "statistics": {
            "total_tasks": total, **contagem,
            "overdue": overdue, "high_priority": high_priority,
            "completion_rate": round((contagem["done"] / total) * 100, 2) if total > 0 else 0,
        },
    }


def listar_categorias():
    result = []
    for c in Category.query.all():
        data = c.to_dict()
        data["task_count"] = Task.query.filter_by(category_id=c.id).count()
        result.append(data)
    return result


def criar_categoria(dados):
    if not dados or not dados.get("name"):
        raise ValidationError("Nome é obrigatório")
    category = Category()
    category.name = dados["name"]
    category.description = dados.get("description", "")
    category.color = dados.get("color", "#000000")
    db.session.add(category)
    db.session.commit()
    return category.to_dict()


def atualizar_categoria(cat_id, dados):
    cat = db.session.get(Category, cat_id)
    if not cat:
        raise ValidationError("Categoria não encontrada", 404)
    if "name" in dados:
        cat.name = dados["name"]
    if "description" in dados:
        cat.description = dados["description"]
    if "color" in dados:
        cat.color = dados["color"]
    db.session.commit()
    return cat.to_dict()


def deletar_categoria(cat_id):
    cat = db.session.get(Category, cat_id)
    if not cat:
        raise ValidationError("Categoria não encontrada", 404)
    db.session.delete(cat)
    db.session.commit()
