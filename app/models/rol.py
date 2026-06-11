from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class Rol(SQLModel, table=True):
    __tablename__ = "rol"

    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(unique=True, index=True)
    nombre: str
    descripcion: Optional[str] = None

    usuarios: List["UsuarioRol"] = Relationship(back_populates="rol")