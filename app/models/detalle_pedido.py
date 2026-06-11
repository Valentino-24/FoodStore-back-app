from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

class DetallePedido(SQLModel, table=True):
    __tablename__ = "detalle_pedido"

    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedido.id")
    producto_id: int = Field(foreign_key="producto.id")

    nombre_producto: str
    precio_unitario: float
    cantidad: int
    subtotal: float

    pedido: Optional["Pedido"] = Relationship(back_populates="detalles")
    producto: Optional["Producto"] = Relationship()