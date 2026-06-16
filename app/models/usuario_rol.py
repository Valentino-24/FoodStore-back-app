from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

class UsuarioRol(SQLModel, table=True):
    __tablename__ = "usuario_rol"

    usuario_id: Optional[int] = Field(
        default=None, foreign_key="usuario.id", primary_key=True
    )
    rol_id: Optional[int] = Field(
        default=None, foreign_key="rol.id", primary_key=True
    )
    asignado_por_id: Optional[int] = Field(
        default=None, foreign_key="usuario.id"
    )
    expires_at: Optional[datetime] = Field(default=None)

    usuario: Optional["Usuario"] = Relationship(
        back_populates="roles",
        sa_relationship_kwargs={"foreign_keys": "UsuarioRol.usuario_id"},
    )
    rol: Optional["Rol"] = Relationship(back_populates="usuarios")