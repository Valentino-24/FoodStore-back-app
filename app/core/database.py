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
        ("producto", "unidad_venta_id", "BIGINT"),
        ("producto_ingrediente", "cantidad", "FLOAT"),
        ("producto_ingrediente", "unidad_medida_id", "BIGINT"),
        ("detalle_pedido", "subtotal_snap", "FLOAT"),
        ("detalle_pedido", "personalizacion", "VARCHAR(500)"),
        ("usuario", "apellido", "VARCHAR(255)"),
        ("usuario", "celular", "VARCHAR(50)"),
        ("usuario_rol", "asignado_por_id", "BIGINT"),
        ("usuario_rol", "expires_at", "TIMESTAMP WITHOUT TIME ZONE"),
        ("ingrediente", "stock_cantidad", "INTEGER"),
        ("pedido", "subtotal", "FLOAT"),
        ("pedido", "descuento", "FLOAT"),
        ("estado_pedido", "es_terminal", "BOOLEAN"),
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