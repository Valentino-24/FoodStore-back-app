from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks

from app.schemas.pedido import PedidoCreate, CambioEstadoRequest
from app.models.usuario import Usuario
from app.services import pedido_service, notificacion_service
from app.core.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])

@router.post("/")
def create_pedido(
    data: PedidoCreate,
    usuario: Usuario = Depends(get_current_user),
    background_tasks: BackgroundTasks = None,
):

    resultado = pedido_service.create_pedido(usuario, data)
    background_tasks.add_task(
        notificacion_service.notificar_nuevo_pedido,
        resultado["id"],
        usuario.id,
        resultado.get("total", 0),
    )
    return resultado

@router.get("/")
def list_pedidos(
    usuario: Usuario = Depends(get_current_user),
):

    return pedido_service.list_pedidos(usuario)

@router.get("/{pedido_id}")
def get_pedido(
    pedido_id: int,
    usuario: Usuario = Depends(get_current_user),
):
    return pedido_service.get_pedido(pedido_id, usuario)

@router.delete("/{pedido_id}")
def delete_pedido(
    pedido_id: int,
    usuario: Usuario = Depends(get_current_user),
    background_tasks: BackgroundTasks = None,
):

    resultado = pedido_service.delete_pedido(pedido_id, usuario)
    background_tasks.add_task(
        notificacion_service.notificar_cambio_estado,
        pedido_id,
        usuario.id,
        "CANCELADO",
        "Pedido cancelado por el cliente",
    )
    return resultado


@router.patch("/{pedido_id}/estado")
def cambiar_estado(
    pedido_id: int,
    data: CambioEstadoRequest,
    usuario: Usuario = Depends(get_current_user),
    background_tasks: BackgroundTasks = None,
):

    resultado = pedido_service.cambiar_estado_pedido(
        pedido_id, data.nuevo_estado_id, usuario, data.observacion
    )

    estado_actual = resultado.get("estado_actual", {})
    background_tasks.add_task(
        notificacion_service.notificar_cambio_estado,
        pedido_id,
        resultado.get("usuario_id"),
        estado_actual.get("codigo", ""),
        data.observacion,
    )
    return resultado

@router.get("/{pedido_id}/historial")
def get_historial(
    pedido_id: int,
    usuario: Usuario = Depends(get_current_user),
):

    return pedido_service.get_historial_pedido(pedido_id, usuario)

@router.get("/{pedido_id}/estados-posibles")
def get_estados_posibles(
    pedido_id: int,
    usuario: Usuario = Depends(get_current_user),
):

    return pedido_service.get_estados_posibles(pedido_id, usuario)