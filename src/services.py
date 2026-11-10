"""Сервисный слой системы учёта заявок.

Вся бизнес-логика — здесь. Роутеры (API) и представления (UI)
только вызывают эти функции и маппят исключения в HTTP-коды.
"""
from datetime import datetime
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .models import User, Category, Status, Request, Comment


# ---------- Исключения ----------

class ServiceError(Exception):
    """Базовое исключение сервисного слоя."""


class NotFoundError(ServiceError):
    """Запись не найдена."""


class ValidationError(ServiceError):
    """Некорректные входные данные."""


class ConflictError(ServiceError):
    """Нарушение уникальности или бизнес-правила."""


# ---------- Справочники ----------

def list_users(db: Session) -> list[User]:
    return db.query(User).order_by(User.id).all()


def list_categories(db: Session) -> list[Category]:
    return db.query(Category).order_by(Category.id).all()


def list_statuses(db: Session) -> list[Status]:
    return db.query(Status).order_by(Status.id).all()


def get_user(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise NotFoundError(f"Пользователь id={user_id} не найден")
    return user


# ---------- Заявки ----------

def list_requests(
    db: Session,
    status_id: int | None = None,
    category_id: int | None = None,
    executor_id: int | None = None,
    search: str | None = None,
) -> list[Request]:
    """Список заявок с фильтрацией и поиском по title/description."""
    q = db.query(Request)

    if status_id is not None:
        q = q.filter(Request.status_id == status_id)
    if category_id is not None:
        q = q.filter(Request.category_id == category_id)
    if executor_id is not None:
        q = q.filter(Request.executor_id == executor_id)
    if search:
        pattern = f"%{search.strip()}%"
        q = q.filter(or_(Request.title.ilike(pattern), Request.description.ilike(pattern)))

    return q.order_by(Request.created_at.desc(), Request.id.desc()).all()


def get_request(db: Session, request_id: int) -> Request:
    req = db.get(Request, request_id)
    if req is None:
        raise NotFoundError(f"Заявка id={request_id} не найдена")
    return req


def _validate_request_refs(
    db: Session,
    category_id: int | None = None,
    status_id: int | None = None,
    applicant_id: int | None = None,
    executor_id: int | None = None,
) -> None:
    """Проверяет существование связанных записей. Кидает ValidationError."""
    if category_id is not None and db.get(Category, category_id) is None:
        raise ValidationError(f"Категория id={category_id} не существует")
    if status_id is not None and db.get(Status, status_id) is None:
        raise ValidationError(f"Статус id={status_id} не существует")
    if applicant_id is not None and db.get(User, applicant_id) is None:
        raise ValidationError(f"Заявитель id={applicant_id} не существует")
    if executor_id is not None:
        executor = db.get(User, executor_id)
        if executor is None:
            raise ValidationError(f"Исполнитель id={executor_id} не существует")
        if executor.role != "executor":
            raise ValidationError(
                f"Пользователь id={executor_id} не является исполнителем (role={executor.role})"
            )


def create_request(
    db: Session,
    title: str,
    description: str | None,
    category_id: int,
    status_id: int,
    applicant_id: int,
    executor_id: int | None = None,
) -> Request:
    if not title or not title.strip():
        raise ValidationError("Поле title обязательно и не может быть пустым")
    if len(title) > 200:
        raise ValidationError("Поле title не должно превышать 200 символов")

    _validate_request_refs(db, category_id, status_id, applicant_id, executor_id)

    req = Request(
        title=title.strip(),
        description=(description or "").strip() or None,
        created_at=datetime.utcnow().isoformat(timespec="seconds"),
        category_id=category_id,
        status_id=status_id,
        applicant_id=applicant_id,
        executor_id=executor_id,
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


def update_request(
    db: Session,
    request_id: int,
    title: str | None = None,
    description: str | None = None,
    category_id: int | None = None,
    status_id: int | None = None,
    executor_id: int | None = None,
) -> Request:
    req = get_request(db, request_id)

    if title is not None:
        if not title.strip():
            raise ValidationError("Поле title не может быть пустым")
        req.title = title.strip()

    if description is not None:
        req.description = description.strip() or None

    _validate_request_refs(
        db,
        category_id=category_id,
        status_id=status_id,
        executor_id=executor_id,
    )

    if category_id is not None:
        req.category_id = category_id
    if status_id is not None:
        req.status_id = status_id
    if executor_id is not None:
        req.executor_id = executor_id

    db.commit()
    db.refresh(req)
    return req


def change_status(db: Session, request_id: int, status_id: int) -> Request:
    req = get_request(db, request_id)
    if db.get(Status, status_id) is None:
        raise ValidationError(f"Статус id={status_id} не существует")
    req.status_id = status_id
    db.commit()
    db.refresh(req)
    return req


def assign_executor(db: Session, request_id: int, user_id: int) -> Request:
    req = get_request(db, request_id)
    user = db.get(User, user_id)
    if user is None:
        raise ValidationError(f"Пользователь id={user_id} не существует")
    if user.role != "executor":
        raise ValidationError(f"Пользователь id={user_id} не является исполнителем")
    req.executor_id = user_id
    db.commit()
    db.refresh(req)
    return req


def add_comment(db: Session, request_id: int, user_id: int, text: str) -> Comment:
    get_request(db, request_id)
    if db.get(User, user_id) is None:
        raise ValidationError(f"Пользователь id={user_id} не существует")
    if not text or not text.strip():
        raise ValidationError("Текст комментария не может быть пустым")

    comment = Comment(
        request_id=request_id,
        user_id=user_id,
        text=text.strip(),
        created_at=datetime.utcnow().isoformat(timespec="seconds"),
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def delete_request(db: Session, request_id: int) -> None:
    req = get_request(db, request_id)
    db.delete(req)
    db.commit()