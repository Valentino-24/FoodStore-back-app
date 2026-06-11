from fastapi import APIRouter, Depends, HTTPException

from app.schemas.ingrediente import IngredienteCreate, IngredienteRead, IngredienteUpdate
from app.services import ingrediente_service
from app.models.usuario import Usuario
from app.core.dependencies import require_admin, require_any

router = APIRouter(prefix="/ingredientes", tags=["Ingredientes"])

@router.get("/", response_model=list[IngredienteRead])
def get_ingredientes(_: Usuario = Depends(require_any)):

    return ingrediente_service.get_all_ingredientes()

@router.get("/{ingrediente_id}", response_model=IngredienteRead)
def get_ingrediente(ingrediente_id: int):

    ingrediente = ingrediente_service.get_ingrediente(ingrediente_id)
    if not ingrediente:
        raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
    return ingrediente

@router.post("/", response_model=IngredienteRead)
def create_ingrediente(
    data: IngredienteCreate,
    _: Usuario = Depends(require_admin),
):
    return ingrediente_service.create_ingrediente(data)

@router.put("/{ingrediente_id}", response_model=IngredienteRead)
def update_ingrediente(
    ingrediente_id: int,
    data: IngredienteUpdate,
    _: Usuario = Depends(require_admin),
):
    ingrediente = ingrediente_service.update_ingrediente(ingrediente_id, data)
    if not ingrediente:
        raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
    return ingrediente

@router.delete("/{ingrediente_id}")
def delete_ingrediente(
    ingrediente_id: int,
    _: Usuario = Depends(require_admin),
):
    result = ingrediente_service.delete_ingrediente(ingrediente_id)
    if not result:
        raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
    return {"ok": True}