from typing import Optional

from sqlmodel import SQLModel

class UsuarioCreate(SQLModel):
    email: str
    password: str
    nombre: str
    apellido: Optional[str] = None
    celular: Optional[str] = None

class UsuarioRead(SQLModel):
    id: int
    email: str
    nombre: str
    apellido: Optional[str] = None
    celular: Optional[str] = None
    rol: str

class LoginRequest(SQLModel):
    email: str
    password: str

class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioRead