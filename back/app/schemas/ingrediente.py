from typing import Optional
from sqlmodel import SQLModel


class IngredienteCreate(SQLModel):
    nombre: str
    descripcion: Optional[str] = None
    es_alergeno: bool = False


class IngredienteRead(SQLModel):
    id: int
    nombre: str
    descripcion: Optional[str]
    es_alergeno: bool


class IngredienteUpdate(SQLModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    es_alergeno: Optional[bool] = None