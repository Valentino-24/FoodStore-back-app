from typing import Optional
from sqlmodel import SQLModel, Field

class FormaPago(SQLModel, table=True):
    __tablename__ = "forma_pago"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    codigo: str = Field(unique=True)