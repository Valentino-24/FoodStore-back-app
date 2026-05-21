from fastapi import APIRouter, HTTPException

from app.schemas.categoria import CategoriaCreate, CategoriaRead, CategoriaUpdate
from app.services import categoria_service

router = APIRouter(prefix="/categorias", tags=["Categorias"])


@router.post("/", response_model=CategoriaRead)
def create_categoria(data: CategoriaCreate):
    return categoria_service.create_categoria(data)


@router.get("/", response_model=list[CategoriaRead])
def get_categorias():
    return categoria_service.get_all_categorias()


@router.get("/{categoria_id}", response_model=CategoriaRead)
def get_categoria(categoria_id: int):
    categoria = categoria_service.get_categoria(categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")
    return categoria


@router.put("/{categoria_id}", response_model=CategoriaRead)
def update_categoria(
    categoria_id: int,
    data: CategoriaUpdate,
):
    categoria = categoria_service.update_categoria(categoria_id, data)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")
    return categoria


@router.delete("/{categoria_id}")
def delete_categoria(categoria_id: int):
    result = categoria_service.delete_categoria(categoria_id)
    if not result:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")
    return {"ok": True}
