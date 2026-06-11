from typing import Optional, List
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship

class Ingrediente(SQLModel, table=True):
    __tablename__ = "ingrediente"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    descripcion: Optional[str] = None
    es_alergeno: bool = False
    deleted_at: Optional[datetime] = Field(default=None, sa_column_kwargs={"nullable": True})

    productos: List["ProductoIngrediente"] = Relationship(back_populates="ingrediente")