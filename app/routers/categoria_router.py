from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.schemas.categoria import CategoriaCreate, CategoriaRead, CategoriaUpdate
from app.services import categoria_service
from app.models.usuario import Usuario
from app.core.dependencies import require_admin, require_any

router = APIRouter(prefix="/categorias", tags=["Categorias"])

@router.get("/", response_model=dict)
def get_categorias_publicas(
    parent_id: Optional[int] = Query(None, description="Filtrar por categoría padre"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):

    return categoria_service.get_categorias_publicas(
        parent_id=parent_id, skip=skip, limit=limit
    )

@router.get("/all", response_model=list[CategoriaRead])
def get_all_categorias(
    _: Usuario = Depends(require_any),
):

    return categoria_service.get_all_categorias()

@router.get("/{categoria_id}", response_model=CategoriaRead)
def get_categoria(categoria_id: int):

    categoria = categoria_service.get_categoria(categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")
    return categoria

@router.post("/", response_model=CategoriaRead)
def create_categoria(
    data: CategoriaCreate,
    _: Usuario = Depends(require_admin),
):
    return categoria_service.create_categoria(data)

@router.put("/{categoria_id}", response_model=CategoriaRead)
def update_categoria(
    categoria_id: int,
    data: CategoriaUpdate,
    _: Usuario = Depends(require_admin),
):
    categoria = categoria_service.update_categoria(categoria_id, data)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")
    return categoria

@router.delete("/{categoria_id}")
def delete_categoria(
    categoria_id: int,
    _: Usuario = Depends(require_admin),
):

    result = categoria_service.delete_categoria(categoria_id)
    if not result:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")
    return {"ok": True}