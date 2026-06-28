from typing import Optional, List
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship, Column
from app.core.db_types import CompatibleArray

class Producto(SQLModel, table=True):
    __tablename__ = "producto"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    descripcion: Optional[str] = None
    precio_base: float
    imagenes: Optional[str] = None
    imagenes_url: Optional[List[str]] = Field(
        default=None, sa_column=Column(CompatibleArray())
    )
    imagenes_public_id: Optional[List[str]] = Field(
        default=None, sa_column=Column(CompatibleArray())
    )
    stock_cantidad: int
    disponible: bool = True
    unidad_venta_id: Optional[int] = Field(default=None, foreign_key="unidad_medida.id")
    deleted_at: Optional[datetime] = Field(default=None, sa_column_kwargs={"nullable": True})

    categorias: List["ProductoCategoria"] = Relationship(back_populates="producto")
    ingredientes: List["ProductoIngrediente"] = Relationship(back_populates="producto")