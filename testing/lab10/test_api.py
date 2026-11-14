"""Автотесты для системы учёта заявок (ЛР №10).

Категории:
- Бизнес-логика (сервисный слой): test_service_*
- API: test_api_*
- Валидация/негативные: test_api_create_* / test_api_validation_*
- Регрессионные: test_regression_*

Запуск: python -m pytest testing/lab10/test_api.py -v
"""
import pytest

from src import services
from src.services import NotFoundError, ValidationError


# ============================================================
# 1. Бизнес-логика (сервисный слой) — минимум 3
# ============================================================

def test_service_list_requests(db_session):
    """Список заявок возвращает все 5 из seed."""
    requests = services.list_requests(db_session)
    assert len(requests) == 5
    assert all(r.title for r in requests)


def test_service_create_request(db_session):
    """Создание заявки через сервис возвращает объект с id."""
    req = services.create_request(
        db_session,
        title="Сервисный тест",
        description="Описание",
        category_id=1,
        status_id=1,
        applicant_id=4,
    )
    assert req.id is not None
    assert req.title == "Сервисный тест"
    assert req.status_id == 1


def test_service_search_requests(db_session):
    """Поиск по title находит заявку «Настроить VPN»."""
    results = services.list_requests(db_session, search="VPN")
    assert len(results) == 1
    assert results[0].title == "Настроить VPN"


def test_service_change_status(db_session):
    """Смена статуса через сервис сохраняется."""
    req = services.change_status(db_session, request_id=1, status_id=2)
    assert req.status_id == 2


# ============================================================
# 2. API — минимум 3 (успешный, ошибочный, 404)
# ============================================================

def test_api_list_requests(client):
    """GET /api/requests → 200, 5 заявок."""
    response = client.get("/api/requests")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5


def test_api_get_request_ok(client):
    """GET /api/requests/1 → 200, заявка «Не работает принтер»."""
    response = client.get("/api/requests/1")
    assert response.status_code == 200
    assert response.json()["title"] == "Не работает принтер"


def test_api_create_request(client):
    """POST /api/requests → 201, заявка создана."""
    response = client.post(
        "/api/requests",
        json={
            "title": "API-тест",
            "description": "Создано в тесте",
            "category_id": 1,
            "status_id": 1,
            "applicant_id": 4,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "API-тест"
    assert data["id"] is not None


def test_api_delete_request(client):
    """DELETE /api/requests/6 → 204, заявка удалена."""
    # Сначала создаём
    create = client.post(
        "/api/requests",
        json={
            "title": "На удаление",
            "category_id": 1,
            "status_id": 1,
            "applicant_id": 4,
        },
    )
    assert create.status_code == 201
    new_id = create.json()["id"]

    # Удаляем
    response = client.delete(f"/api/requests/{new_id}")
    assert response.status_code == 204


# ============================================================
# 3. Валидация / негативные — минимум 2
# ============================================================

def test_api_create_empty_title(client):
    """POST с пустым title → 422."""
    response = client.post(
        "/api/requests",
        json={"title": "", "category_id": 1, "status_id": 1, "applicant_id": 4},
    )
    assert response.status_code == 422


def test_api_create_invalid_category(client):
    """POST с несуществующей категорией → 422."""
    response = client.post(
        "/api/requests",
        json={"title": "Тест", "category_id": 999, "status_id": 1, "applicant_id": 4},
    )
    assert response.status_code == 422
    assert "не существует" in response.json()["detail"].lower()


def test_api_get_request_not_found(client):
    """GET несуществующей заявки → 404."""
    response = client.get("/api/requests/99999")
    assert response.status_code == 404
    assert "не найдена" in response.json()["detail"].lower()


def test_api_assign_non_executor(client):
    """Назначение пользователя без роли executor → 422."""
    response = client.post(
        "/api/requests/1/assign",
        json={"user_id": 4},  # user 4 — applicant, не executor
    )
    assert response.status_code == 422
    assert "исполнител" in response.json()["detail"].lower()


# ============================================================
# 4. Регрессионные — минимум 2
# ============================================================

def test_regression_health(client):
    """Health-check всегда 200 (не сломался при изменениях)."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_regression_search_after_status_change(client):
    """Поиск работает после смены статуса (регресс на связанность)."""
    # Меняем статус заявки 1
    resp = client.post("/api/requests/1/status", json={"status_id": 2})
    assert resp.status_code == 200

    # Поиск по VPN (заявка 5) не должен сломаться
    search = client.get("/api/requests?search=VPN")
    assert search.status_code == 200
    assert len(search.json()) == 1


def test_regression_filters_combined(client):
    """Комбинация фильтров status_id + search работает."""
    response = client.get("/api/requests?status_id=2&search=VPN")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Настроить VPN"


def test_regression_integration_create_read(client):
    """Интеграция: создание → чтение → данные сохранены."""
    create = client.post(
        "/api/requests",
        json={
            "title": "Интеграционный",
            "description": "Проверка сохранения",
            "category_id": 1,
            "status_id": 1,
            "applicant_id": 4,
        },
    )
    assert create.status_code == 201
    new_id = create.json()["id"]

    read = client.get(f"/api/requests/{new_id}")
    assert read.status_code == 200
    assert read.json()["title"] == "Интеграционный"