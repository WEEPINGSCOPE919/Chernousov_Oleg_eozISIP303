"""Фикстуры для pytest: in-memory SQLite, тестовый клиент FastAPI.

Тесты НЕ трогают реальную request_system.db и НЕ ходят на Render.
Для каждого теста создаётся свежая БД в памяти, наполняется из schema.sql + seed.sql,
после теста уничтожается.
"""
import os
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.db import Base, get_db
from src.main import app

# Путь к schema.sql и seed.sql — относительно корня проекта
ROOT = Path(__file__).resolve().parent.parent
SCHEMA_SQL = ROOT / "docs" / "db" / "schema.sql"
SEED_SQL = ROOT / "docs" / "db" / "seed.sql"


@pytest.fixture()
def db_engine():
    """Создаёт in-memory SQLite, наполняет из schema.sql + seed.sql."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    # Создаём таблицы из schema.sql (как в проде, с DEFAULT datetime('now'))
    with engine.begin() as conn:
        with open(SCHEMA_SQL, "r", encoding="utf-8") as f:
            conn.connection.executescript(f.read())

    # Наполняем тестовыми данными из seed.sql
    with engine.begin() as conn:
        with open(SEED_SQL, "r", encoding="utf-8") as f:
            conn.connection.executescript(f.read())

    yield engine
    engine.dispose()


@pytest.fixture()
def db_session(db_engine):
    """Сессия SQLAlchemy для тестов бизнес-логики."""
    TestingSessionLocal = sessionmaker(
        bind=db_engine, autoflush=False, autocommit=False
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_engine):
    """TestClient FastAPI с подменённым get_db (in-memory БД)."""
    TestingSessionLocal = sessionmaker(
        bind=db_engine, autoflush=False, autocommit=False
    )

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