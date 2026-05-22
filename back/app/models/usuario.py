from typing import Optional, List
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field, Relationship


class Usuario(SQLModel, table=True):
    __tablename__ = "usuario"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    nombre: str
    rol: str = Field(default="CLIENT")  # Rol principal para compatibilidad
    deleted_at: Optional[datetime] = Field(default=None, sa_column_kwargs={"nullable": True})

    # RBAC many-to-many via UsuarioRol
    roles: List["UsuarioRol"] = Relationship(back_populates="usuario")

    # Otras relaciones
    pedidos: List["Pedido"] = Relationship(back_populates="usuario")
    direcciones: List["DireccionEntrega"] = Relationship(back_populates="usuario")
