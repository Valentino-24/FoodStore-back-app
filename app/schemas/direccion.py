from typing import Optional
from sqlmodel import SQLModel

class DireccionCreate(SQLModel):
    alias: str
    direccion: str
    ciudad: str
    codigo_postal: Optional[str] = None
    es_principal: bool = False

class DireccionUpdate(SQLModel):
    alias: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    codigo_postal: Optional[str] = None
    es_principal: Optional[bool] = None

class DireccionRead(SQLModel):
    id: int
    usuario_id: int
    alias: str
    direccion: str
    ciudad: str
    codigo_postal: Optional[str] = None
    es_principal: bool