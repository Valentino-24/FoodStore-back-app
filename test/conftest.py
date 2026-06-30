import os
import pytest

# Force SQLite in-memory BEFORE any app import
os.environ["DATABASE_URL"] = "sqlite://"

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
    return test_engine


@pytest.fixture(scope="session", autouse=True)
def _init_app_db(engine):
    """Inicializa la DB de la app con el engine de test y ejecuta el seed."""
    import app.core.database as db_mod
    import app.core.uow as uow_mod

    # Reemplazar engines para que toda la app use el engine de test
    original_db_engine = db_mod.engine
    original_uow_engine = uow_mod.engine
    db_mod.engine = engine
    uow_mod.engine = engine

    # Ejecutar seed (roles, estados, etc.) en el engine de test
    from app.db.seed import seed_all
    seed_all()

    yield

    db_mod.engine = original_db_engine
    uow_mod.engine = original_uow_engine


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
