from typing import Optional
from sqlmodel import SQLModel, Field


class UnidadMedida(SQLModel, table=True):
    __tablename__ = "unidad_medida"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(unique=True, index=True)
    simbolo: str = Field(unique=True)
    tipo: str  # peso, volumen, contable
