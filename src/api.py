from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from .db import get_db
from . import services
from .services import NotFoundError, ValidationError, ConflictError
from .schemas import (
    RequestOut, RequestCreate, RequestUpdate, StatusChange,
    AssignExecutor, CommentCreate, CommentOut,
    UserOut, CategoryOut, StatusOut, ErrorResponse,
)

router = APIRouter(prefix="/api", tags=["requests"])


def _handle_service_error(e: Exception) -> HTTPException:
    if isinstance(e, NotFoundError):
        return HTTPException(status_code=404, detail=str(e))
    if isinstance(e, ValidationError):
        return HTTPException(status_code=422, detail=str(e))
    if isinstance(e, ConflictError):
        return HTTPException(status_code=409, detail=str(e))
    return HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


# ---------- Справочники ----------

@router.get("/users", response_model=list[UserOut], summary="Список пользователей")
def api_list_users(db: Session = Depends(get_db)):
    return services.list_users(db)


@router.get("/categories", response_model=list[CategoryOut], summary="Справочник категорий")
def api_list_categories(db: Session = Depends(get_db)):
    return services.list_categories(db)


@router.get("/statuses", response_model=list[StatusOut], summary="Справочник статусов")
def api_list_statuses(db: Session = Depends(get_db)):
    return services.list_statuses(db)


# ---------- Заявки ----------

@router.get("/requests", response_model=list[RequestOut], summary="Список заявок с фильтрами")
def api_list_requests(
    status_id: int | None = Query(None, description="Фильтр по статусу"),
    category_id: int | None = Query(None, description="Фильтр по категории"),
    executor_id: int | None = Query(None, description="Фильтр по исполнителю"),
    search: str | None = Query(None, description="Поиск по title/description"),
    db: Session = Depends(get_db),
):
    return services.list_requests(db, status_id, category_id, executor_id, search)


@router.get(
    "/requests/{request_id}",
    response_model=RequestOut,
    summary="Получить заявку",
    responses={404: {"model": ErrorResponse}},
)
def api_get_request(request_id: int, db: Session = Depends(get_db)):
    try:
        return services.get_request(db, request_id)
    except Exception as e:
        raise _handle_service_error(e)


@router.post(
    "/requests",
    response_model=RequestOut,
    status_code=status.HTTP_201_CREATED,
    summary="Создать заявку",
    responses={422: {"model": ErrorResponse}},
)
def api_create_request(payload: RequestCreate, db: Session = Depends(get_db)):
    try:
        return services.create_request(
            db,
            title=payload.title,
            description=payload.description,
            category_id=payload.category_id,
            status_id=payload.status_id,
            applicant_id=payload.applicant_id,
            executor_id=payload.executor_id,
        )
    except Exception as e:
        raise _handle_service_error(e)


@router.patch(
    "/requests/{request_id}",
    response_model=RequestOut,
    summary="Изменить заявку",
    responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def api_update_request(
    request_id: int, payload: RequestUpdate, db: Session = Depends(get_db)
):
    try:
        return services.update_request(
            db,
            request_id=request_id,
            title=payload.title,
            description=payload.description,
            category_id=payload.category_id,
            status_id=payload.status_id,
            executor_id=payload.executor_id,
        )
    except Exception as e:
        raise _handle_service_error(e)


@router.delete(
    "/requests/{request_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить заявку",
    responses={404: {"model": ErrorResponse}},
)
def api_delete_request(request_id: int, db: Session = Depends(get_db)):
    try:
        services.delete_request(db, request_id)
    except Exception as e:
        raise _handle_service_error(e)


@router.post(
    "/requests/{request_id}/status",
    response_model=RequestOut,
    summary="Сменить статус",
    responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def api_change_status(
    request_id: int, payload: StatusChange, db: Session = Depends(get_db)
):
    try:
        return services.change_status(db, request_id, payload.status_id)
    except Exception as e:
        raise _handle_service_error(e)


@router.post(
    "/requests/{request_id}/assign",
    response_model=RequestOut,
    summary="Назначить исполнителя",
    responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def api_assign_executor(
    request_id: int, payload: AssignExecutor, db: Session = Depends(get_db)
):
    try:
        return services.assign_executor(db, request_id, payload.user_id)
    except Exception as e:
        raise _handle_service_error(e)


@router.post(
    "/requests/{request_id}/comments",
    response_model=CommentOut,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить комментарий",
    responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def api_add_comment(
    request_id: int, payload: CommentCreate, db: Session = Depends(get_db)
):
    try:
        return services.add_comment(db, request_id, payload.user_id, payload.text)
    except Exception as e:
        raise _handle_service_error(e)