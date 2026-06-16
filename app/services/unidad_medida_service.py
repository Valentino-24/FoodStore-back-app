from typing import Optional, List

from fastapi import HTTPException
from sqlmodel import select

from app.core.uow import UnitOfWork
from app.models.unidad_medida import UnidadMedida
from app.models.producto import Producto


def listar_todas() -> List[UnidadMedida]:
    with UnitOfWork() as uow:
        return uow.unidades_medida.get_all()


def obtener_por_id(unidad_id: int) -> Optional[UnidadMedida]:
    with UnitOfWork() as uow:
        return uow.unidades_medida.get_by_id(unidad_id)


def crear_unidad(data) -> UnidadMedida:
    with UnitOfWork() as uow:
        # Validar que no exista el mismo nombre o símbolo
        existentes = uow.unidades_medida.get_all()
        for u in existentes:
            if u.nombre.lower() == data.nombre.lower():
                raise HTTPException(
                    status_code=400,
                    detail=f"Ya existe una unidad con el nombre '{data.nombre}'",
                )
            if u.simbolo.lower() == data.simbolo.lower():
                raise HTTPException(
                    status_code=400,
                    detail=f"Ya existe una unidad con el símbolo '{data.simbolo}'",
                )

        unidad = UnidadMedida(
            nombre=data.nombre,
            simbolo=data.simbolo,
            tipo=data.tipo,
        )
        uow.unidades_medida.create(unidad)
        return unidad


def actualizar_unidad(unidad_id: int, data) -> Optional[UnidadMedida]:
    with UnitOfWork() as uow:
        unidad = uow.unidades_medida.get_by_id(unidad_id)
        if not unidad:
            return None

        if data.nombre is not None:
            unidad.nombre = data.nombre
        if data.simbolo is not None:
            unidad.simbolo = data.simbolo
        if data.tipo is not None:
            unidad.tipo = data.tipo

        uow.unidades_medida.update(unidad)
        return unidad


def eliminar_unidad(unidad_id: int) -> None:
    with UnitOfWork() as uow:
        unidad = uow.unidades_medida.get_by_id(unidad_id)
        if not unidad:
            raise HTTPException(status_code=404, detail="Unidad de medida no encontrada")

        # Verificar que no esté siendo usada por algún producto
        productos = uow.session.exec(
            select(Producto).where(Producto.unidad_venta_id == unidad_id)
        ).all()
        if productos:
            raise HTTPException(
                status_code=400,
                detail=f"No se puede eliminar la unidad porque está siendo usada por {len(productos)} producto(s)",
            )

        uow.unidades_medida.delete(unidad)
