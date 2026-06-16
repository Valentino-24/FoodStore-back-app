from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.schemas.unidad_medida import (
    UnidadMedidaCreate,
    UnidadMedidaRead,
    UnidadMedidaUpdate,
)
from app.services import unidad_medida_service
from app.models.usuario import Usuario
from app.core.dependencies import require_admin

router = APIRouter(prefix="/unidades-medida", tags=["Unidades de Medida"])


@router.get("/", response_model=List[UnidadMedidaRead])
def listar_unidades():
    return unidad_medida_service.listar_todas()


@router.get("/{unidad_id}", response_model=UnidadMedidaRead)
def obtener_unidad(unidad_id: int):
    unidad = unidad_medida_service.obtener_por_id(unidad_id)
    if not unidad:
        raise HTTPException(status_code=404, detail="Unidad de medida no encontrada")
    return unidad


@router.post("/", response_model=UnidadMedidaRead, status_code=201)
def crear_unidad(
    data: UnidadMedidaCreate,
    _: Usuario = Depends(require_admin),
):
    return unidad_medida_service.crear_unidad(data)


@router.put("/{unidad_id}", response_model=UnidadMedidaRead)
def actualizar_unidad(
    unidad_id: int,
    data: UnidadMedidaUpdate,
    _: Usuario = Depends(require_admin),
):
    unidad = unidad_medida_service.actualizar_unidad(unidad_id, data)
    if not unidad:
        raise HTTPException(status_code=404, detail="Unidad de medida no encontrada")
    return unidad


@router.delete("/{unidad_id}", status_code=204)
def eliminar_unidad(
    unidad_id: int,
    _: Usuario = Depends(require_admin),
):
    unidad_medida_service.eliminar_unidad(unidad_id)
