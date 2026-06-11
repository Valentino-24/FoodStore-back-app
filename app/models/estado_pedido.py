from typing import Optional
from sqlmodel import SQLModel, Field

class EstadoPedido(SQLModel, table=True):
    __tablename__ = "estado_pedido"

    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(unique=True, index=True)

    nombre: str
    orden: int