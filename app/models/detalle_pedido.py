from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship, Column
from app.core.db_types import CompatibleArray
from sqlalchemy import Integer

class DetallePedido(SQLModel, table=True):
    __tablename__ = "detalle_pedido"

    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedido.id")
    producto_id: int = Field(foreign_key="producto.id")

    nombre_producto: str
    precio_unitario: float
    cantidad: int
    subtotal: float
    subtotal_snap: float = Field(default=0.0)
    personalizacion: Optional[List[int]] = Field(
        default=None, sa_column=Column(CompatibleArray(Integer))
    )

    pedido: Optional["Pedido"] = Relationship(back_populates="detalles")
    producto: Optional["Producto"] = Relationship()