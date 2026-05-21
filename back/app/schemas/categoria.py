from typing import Optional
from sqlmodel import SQLModel


class CategoriaCreate(SQLModel):
    nombre: str
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None
    parent_id: Optional[int] = None


class CategoriaRead(SQLModel):
    id: int
    nombre: str
    descripcion: Optional[str]
    imagen_url: Optional[str]
    parent_id: Optional[int]


class CategoriaUpdate(SQLModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None
    parent_id: Optional[int] = None