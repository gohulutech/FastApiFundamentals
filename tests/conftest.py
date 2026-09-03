"""Shared fixtures for the test suite.

Each test gets an isolated, in-memory SQLite database. The FastAPI app's
`get_session` dependency is overridden to use that in-memory DB, so no test
ever touches the real `carsharing.db` file.

The `session` fixture lets tests seed rows (users, cars, trips) directly into
the same in-memory DB the app reads from.
"""
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from fastapi_fundamentals import carsharing
from fastapi_fundamentals.db import get_session


@pytest.fixture()
def engine():
    """An isolated, in-memory SQLite engine with schema created.

    ``StaticPool`` keeps a single shared connection, so the in-memory database
    is the same for every ``Session`` opened on this engine — otherwise each
    connection would get its own empty database.
    """
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(test_engine)
    yield test_engine
    test_engine.dispose()


@pytest.fixture()
def session(engine) -> Generator[Session, None, None]:
    """A session bound to the isolated test database."""
    with Session(engine) as test_session:
        yield test_session


@pytest.fixture()
def client(engine) -> Generator[TestClient, None, None]:
    """Yield a TestClient wired to the isolated in-memory database."""
    def override_get_session() -> Generator[Session, None, None]:
        with Session(engine) as test_session:
            yield test_session

    carsharing.app.dependency_overrides[get_session] = override_get_session
    try:
        with TestClient(carsharing.app) as test_client:
            yield test_client
    finally:
        carsharing.app.dependency_overrides.clear()
