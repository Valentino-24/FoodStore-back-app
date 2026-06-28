import os
import pytest

# Force SQLite BEFORE any app import — this ensures database.py creates
# a SQLite engine instead of connecting to the real PostgreSQL.
os.environ["DATABASE_URL"] = "sqlite:///test.db"

from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from sqlalchemy import event

from app.main import app
from app.core.database import get_session
from app.core.middleware.rate_limit_middleware import RateLimitMiddleware


@pytest.fixture(scope="session")
def engine():
    """Engine SQLite en memoria compartido por todos los tests."""
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(test_engine)
    yield test_engine


@pytest.fixture(name="session")
def session_fixture(engine):
    """Sesión transaccional con savepoint para rollback por test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(sess, trans):
        if trans.nested and not trans._parent.nested:
            sess.begin_nested()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """TestClient con sesión de BD inyectada y rate limiters reseteados."""
    RateLimitMiddleware.reset_all_limiters()

    def get_session_override():
        yield session

    app.dependency_overrides[get_session] = get_session_override

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
