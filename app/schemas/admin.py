from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel

class UsuarioAdminRead(SQLModel):
    id: int
    email: str
    nombre: str
    rol: str
    deleted_at: Optional[datetime] = None

class UsuarioAdminUpdate(SQLModel):
    nombre: Optional[str] = None
    email: Optional[str] = None
    rol: Optional[str] = None

class UsuarioCreateAdmin(SQLModel):
    email: str
    password: str
    nombre: str
    rol: str = "CLIENT"

class AsignarRolesRequest(SQLModel):
    roles_ids: List[int]