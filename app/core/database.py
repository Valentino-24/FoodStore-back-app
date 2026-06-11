from sqlmodel import SQLModel, create_engine, Session, text
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=True)

def create_db_and_tables():

    SQLModel.metadata.create_all(engine)
    _migrate_existing_tables()

def _migrate_existing_tables():

    migraciones = [
        ("usuario", "deleted_at", "TIMESTAMP WITHOUT TIME ZONE"),
        ("categoria", "deleted_at", "TIMESTAMP WITHOUT TIME ZONE"),
        ("producto", "deleted_at", "TIMESTAMP WITHOUT TIME ZONE"),
        ("ingrediente", "deleted_at", "TIMESTAMP WITHOUT TIME ZONE"),
    ]
    with Session(engine) as session:
        for tabla, columna, tipo in migraciones:
            try:
                session.exec(
                    text(f"ALTER TABLE {tabla} ADD COLUMN IF NOT EXISTS {columna} {tipo}")
                )
                session.commit()
            except Exception:
                session.rollback()

def get_session():
    with Session(engine) as session:
        yield session