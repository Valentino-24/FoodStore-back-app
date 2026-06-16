from typing import Optional
from datetime import date

from fastapi import APIRouter, Depends, Query

from app.models.usuario import Usuario
from app.services import estadistica_service
from app.core.dependencies import require_admin

router = APIRouter(prefix="/estadisticas", tags=["Estadísticas"])


@router.get("/resumen")
def get_resumen(
    _: Usuario = Depends(require_admin),
):
    return estadistica_service.get_resumen()


@router.get("/ventas")
def get_ventas(
    fecha_desde: Optional[date] = Query(None, description="Fecha desde (YYYY-MM-DD)"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha hasta (YYYY-MM-DD)"),
    agrupar_por: str = Query("dia", pattern="^(dia|semana|mes)$"),
    _: Usuario = Depends(require_admin),
):
    return estadistica_service.get_ventas(
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        agrupar_por=agrupar_por,
    )


@router.get("/productos-mas-vendidos")
def get_productos_mas_vendidos(
    limite: int = Query(10, ge=1, le=100),
    _: Usuario = Depends(require_admin),
):
    return estadistica_service.get_productos_mas_vendidos(limite=limite)


@router.get("/pedidos-por-estado")
def get_pedidos_por_estado(
    _: Usuario = Depends(require_admin),
):
    return estadistica_service.get_pedidos_por_estado()
