"""Shared test fixtures. pytest loads this file automatically.

A *fixture* is setup code a test can ask for by naming it as an argument,
the test-side equivalent of FastAPI's dependency injection.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401  (registers all tables on Base.metadata)
from app.core.db import Base, get_db
from app.main import app


@pytest.fixture
def db_session():
    """A brand-new, empty in-memory database for each test."""
    engine = create_engine(
        "sqlite://",  # in memory: disappears when the test ends
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # every connection shares the same in-memory DB
    )
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = TestSession()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
def client(db_session):
    """An HTTP client whose requests use the test database instead of dev.db."""
    app.dependency_overrides[get_db] = lambda: db_session
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
