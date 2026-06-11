from typing import Optional, List
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship

class Producto(SQLModel, table=True):
    __tablename__ = "producto"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    descripcion: Optional[str] = None
    precio_base: float
    imagenes: Optional[str] = None
    stock_cantidad: int
    disponible: bool = True
    deleted_at: Optional[datetime] = Field(default=None, sa_column_kwargs={"nullable": True})

    categorias: List["ProductoCategoria"] = Relationship(back_populates="producto")
    ingredientes: List["ProductoIngrediente"] = Relationship(back_populates="producto")