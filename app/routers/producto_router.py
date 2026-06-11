from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.schemas.producto import ProductoCreate, ProductoRead, ProductoUpdate
from app.services import producto_service
from app.models.usuario import Usuario
from app.core.dependencies import require_admin, require_admin_or_stock, require_any

router = APIRouter(prefix="/productos", tags=["Productos"])

@router.get("/")
def get_productos_publicos(
    categoria_id: Optional[int] = Query(None, description="Filtrar por categoría"),
    disponible: Optional[bool] = Query(None, description="Filtrar por disponibilidad"),
    busqueda: Optional[str] = Query(None, description="Búsqueda por texto"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):

    return producto_service.get_productos_publicos(
        categoria_id=categoria_id,
        disponible=disponible,
        busqueda=busqueda,
        skip=skip,
        limit=limit,
    )

@router.get("/all", response_model=list[ProductoRead])
def get_all_productos(
    _: Usuario = Depends(require_any),
):

    return producto_service.get_productos()

@router.get("/{producto_id}", response_model=ProductoRead)
def get_producto(producto_id: int):

    producto = producto_service.get_producto(producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

@router.post("/", response_model=ProductoRead)
def create_producto(
    data: ProductoCreate,
    _: Usuario = Depends(require_admin),
):

    return producto_service.create_producto(data)

@router.put("/{producto_id}", response_model=ProductoRead)
def update_producto(
    producto_id: int,
    data: ProductoUpdate,
    _: Usuario = Depends(require_admin),
):

    return producto_service.update_producto(producto_id, data)

@router.delete("/{producto_id}")
def delete_producto(
    producto_id: int,
    _: Usuario = Depends(require_admin),
):

    return producto_service.delete_producto(producto_id)

@router.patch("/{producto_id}/disponibilidad")
def toggle_disponibilidad(
    producto_id: int,
    disponible: bool = Query(..., description="Nuevo estado de disponibilidad"),
    _: Usuario = Depends(require_admin_or_stock),
):

    return producto_service.toggle_disponibilidad(producto_id, disponible)