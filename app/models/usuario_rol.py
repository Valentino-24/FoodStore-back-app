from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

class UsuarioRol(SQLModel, table=True):
    __tablename__ = "usuario_rol"

    usuario_id: Optional[int] = Field(
        default=None, foreign_key="usuario.id", primary_key=True
    )
    rol_id: Optional[int] = Field(
        default=None, foreign_key="rol.id", primary_key=True
    )

    usuario: Optional["Usuario"] = Relationship(back_populates="roles")
    rol: Optional["Rol"] = Relationship(back_populates="usuarios")