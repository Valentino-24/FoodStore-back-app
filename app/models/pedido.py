from typing import Optional, List
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship

class Pedido(SQLModel, table=True):
    __tablename__ = "pedido"

    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id")
    fecha_pedido: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    estado_actual_id: int = Field(foreign_key="estado_pedido.id")
    forma_pago_id: int = Field(foreign_key="forma_pago.id")
    direccion_entrega_id: Optional[int] = Field(
        default=None, foreign_key="direccion_entrega.id"
    )
    total: float
    deleted_at: Optional[datetime] = Field(default=None, sa_column_kwargs={"nullable": True})

    usuario: Optional["Usuario"] = Relationship(back_populates="pedidos")
    estado_actual: Optional["EstadoPedido"] = Relationship()
    forma_pago: Optional["FormaPago"] = Relationship()
    direccion: Optional["DireccionEntrega"] = Relationship()
    detalles: List["DetallePedido"] = Relationship(back_populates="pedido")
    historial_estados: List["HistorialEstadoPedido"] = Relationship(back_populates="pedido")