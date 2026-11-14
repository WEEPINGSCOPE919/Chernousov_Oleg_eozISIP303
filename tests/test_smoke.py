"""Smoke-тест: проверяет, что фикстура поднимает БД и клиент."""


def test_client_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_db_session_has_seed_data(db_session):
    from src.models import Request, User
    assert db_session.query(User).count() == 5
    assert db_session.query(Request).count() == 5