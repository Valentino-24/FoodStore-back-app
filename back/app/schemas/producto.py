from typing import Optional, List
from sqlmodel import SQLModel


class CategoriaSimple(SQLModel):
    id: int
    nombre: str
    es_principal: bool = False


class IngredienteSimple(SQLModel):
    id: int
    nombre: str


class CategoriaInput(SQLModel):
    id: int
    es_principal: bool = False


class ProductoCreate(SQLModel):
    nombre: str
    descripcion: Optional[str] = None
    precio_base: float
    imagenes: Optional[str] = None
    stock_cantidad: int
    disponible: bool = True

    categorias: List[CategoriaInput] = []  
    ingredientes_ids: List[int] = []


class ProductoRead(SQLModel):
    id: int
    nombre: str
    descripcion: Optional[str]
    precio_base: float
    imagenes: Optional[str] = None
    stock_cantidad: int
    disponible: bool

    categorias: List[CategoriaSimple] = []
    ingredientes: List[IngredienteSimple] = []


class ProductoUpdate(SQLModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio_base: Optional[float] = None
    imagenes: Optional[str] = None
    stock_cantidad: Optional[int] = None
    disponible: Optional[bool] = None

    categorias: Optional[List[CategoriaInput]] = None
    ingredientes_ids: Optional[List[int]] = None