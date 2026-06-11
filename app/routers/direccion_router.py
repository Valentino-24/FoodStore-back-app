from fastapi import APIRouter, Depends, HTTPException

from app.schemas.direccion import DireccionCreate, DireccionUpdate, DireccionRead
from app.models.usuario import Usuario
from app.services import direccion_service
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/direcciones", tags=["Direcciones"])

@router.post("/", response_model=DireccionRead)
def create_direccion(
    data: DireccionCreate,
    usuario: Usuario = Depends(get_current_user),
):
    return direccion_service.create_direccion(usuario, data)

@router.get("/", response_model=list[DireccionRead])
def list_direcciones(
    usuario: Usuario = Depends(get_current_user),
):
    return direccion_service.list_direcciones(usuario)

@router.get("/{direccion_id}", response_model=DireccionRead)
def get_direccion(
    direccion_id: int,
    usuario: Usuario = Depends(get_current_user),
):
    return direccion_service.get_direccion(direccion_id, usuario)

@router.put("/{direccion_id}", response_model=DireccionRead)
def update_direccion(
    direccion_id: int,
    data: DireccionUpdate,
    usuario: Usuario = Depends(get_current_user),
):
    return direccion_service.update_direccion(direccion_id, usuario, data)

@router.delete("/{direccion_id}")
def delete_direccion(
    direccion_id: int,
    usuario: Usuario = Depends(get_current_user),
):
    result = direccion_service.delete_direccion(direccion_id, usuario)
    return {"ok": True}

@router.patch("/{direccion_id}/principal", response_model=DireccionRead)
def marcar_principal(
    direccion_id: int,
    usuario: Usuario = Depends(get_current_user),
):

    return direccion_service.marcar_principal(direccion_id, usuario)