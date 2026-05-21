from fastapi import APIRouter, HTTPException

from app.schemas.producto import ProductoCreate, ProductoRead, ProductoUpdate
from app.services import producto_service

router = APIRouter(prefix="/productos", tags=["Productos"])


@router.post("/", response_model=ProductoRead)
def create_producto(data: ProductoCreate):
    return producto_service.create_producto(data)


@router.get("/", response_model=list[ProductoRead])
def get_productos():
    return producto_service.get_productos()


@router.get("/{producto_id}", response_model=ProductoRead)
def get_producto(producto_id: int):
    return producto_service.get_producto(producto_id)


@router.put("/{producto_id}", response_model=ProductoRead)
def update_producto(producto_id: int, data: ProductoUpdate):
    return producto_service.update_producto(producto_id, data)


@router.delete("/{producto_id}")
def delete_producto(producto_id: int):
    return producto_service.delete_producto(producto_id)
