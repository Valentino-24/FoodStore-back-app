from typing import Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship

class DireccionEntrega(SQLModel, table=True):
    __tablename__ = "direccion_entrega"

    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id")
    alias: str
    direccion: str
    ciudad: str
    codigo_postal: Optional[str] = None
    es_principal: bool = False
    deleted_at: Optional[datetime] = Field(default=None, sa_column_kwargs={"nullable": True})

    usuario: Optional["Usuario"] = Relationship(back_populates="direcciones")