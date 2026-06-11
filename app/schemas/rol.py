from typing import Optional
from sqlmodel import SQLModel

class RolRead(SQLModel):
    id: int
    codigo: str
    nombre: str
    descripcion: Optional[str] = None

class RolCreate(SQLModel):
    codigo: str
    nombre: str
    descripcion: Optional[str] = None