from typing import Optional, List
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship

class Categoria(SQLModel, table=True):
    __tablename__ = "categoria"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None

    parent_id: Optional[int] = Field(default=None, foreign_key="categoria.id")

    deleted_at: Optional[datetime] = Field(default=None, sa_column_kwargs={"nullable": True})

    parent: Optional["Categoria"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "Categoria.id"}
    )

    children: List["Categoria"] = Relationship(back_populates="parent")