from typing import Optional

from sqlmodel import SQLModel, Field


class Usuario(SQLModel, table=True):
    __tablename__ = "usuario"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    nombre: str
    rol: str = Field(default="user")
