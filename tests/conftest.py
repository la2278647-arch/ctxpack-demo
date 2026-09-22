"""Shared fixtures.

Everything points at an in-memory SQLite database so the suite never writes to
disk and runs in any order.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from hello_service.app import create_app
from hello_service.db import Base, get_session


@pytest.fixture()
def client():
    """A client bound to a fresh in-memory database per test."""
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine, expire_on_commit=False)

    def override():
        s = TestSession()
        try:
            yield s
            s.commit()
        finally:
            s.close()

    app = create_app()
    app.dependency_overrides[get_session] = override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
