from typing import Optional
from sqlmodel import SQLModel


class UnidadMedidaCreate(SQLModel):
    nombre: str
    simbolo: str
    tipo: str


class UnidadMedidaUpdate(SQLModel):
    nombre: Optional[str] = None
    simbolo: Optional[str] = None
    tipo: Optional[str] = None


class UnidadMedidaRead(SQLModel):
    id: int
    nombre: str
    simbolo: str
    tipo: str
