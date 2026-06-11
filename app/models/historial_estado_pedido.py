from typing import Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship

class HistorialEstadoPedido(SQLModel, table=True):

    __tablename__ = "historial_estado_pedido"

    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedido.id")
    estado_anterior_id: Optional[int] = Field(
        default=None, foreign_key="estado_pedido.id"
    )
    estado_nuevo_id: int = Field(foreign_key="estado_pedido.id")
    cambiado_por_id: int = Field(foreign_key="usuario.id")
    fecha_cambio: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    observacion: Optional[str] = None

    pedido: Optional["Pedido"] = Relationship(back_populates="historial_estados")
    estado_anterior: Optional["EstadoPedido"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "HistorialEstadoPedido.estado_anterior_id"}
    )
    estado_nuevo: Optional["EstadoPedido"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "HistorialEstadoPedido.estado_nuevo_id"}
    )
    cambiado_por: Optional["Usuario"] = Relationship()