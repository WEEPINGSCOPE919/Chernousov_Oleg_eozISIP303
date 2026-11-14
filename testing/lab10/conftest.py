"""Фикстуры для pytest: in-memory SQLite, тестовый клиент FastAPI.

Тесты НЕ трогают реальную request_system.db и НЕ ходят на Render.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from pathlib import Path

from src.db import get_db
from src.main import app

ROOT = Path(__file__).resolve().parent.parent.parent
SCHEMA_SQL = ROOT / "docs" / "db" / "schema.sql"
SEED_SQL = ROOT / "docs" / "db" / "seed.sql"


@pytest.fixture()
def db_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    with engine.begin() as conn:
        with open(SCHEMA_SQL, "r", encoding="utf-8") as f:
            conn.connection.executescript(f.read())
    with engine.begin() as conn:
        with open(SEED_SQL, "r", encoding="utf-8") as f:
            conn.connection.executescript(f.read())
    yield engine
    engine.dispose()


@pytest.fixture()
def db_session(db_engine):
    TestingSessionLocal = sessionmaker(bind=db_engine, autoflush=False, autocommit=False)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_engine):
    TestingSessionLocal = sessionmaker(bind=db_engine, autoflush=False, autocommit=False)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
