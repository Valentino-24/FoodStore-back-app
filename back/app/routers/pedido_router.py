from fastapi import APIRouter, Depends, HTTPException

from app.schemas.pedido import PedidoCreate, CambioEstadoRequest
from app.models.usuario import Usuario
from app.services import pedido_service
from app.core.dependencies import get_current_user, require_admin_or_pedidos

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


@router.post("/")
def create_pedido(
    data: PedidoCreate,
    usuario: Usuario = Depends(get_current_user),
):
    """Creación de pedido desde el carrito con transacción atómica."""
    return pedido_service.create_pedido(usuario, data)


@router.get("/")
def list_pedidos(
    usuario: Usuario = Depends(get_current_user),
):
    """
    Lista pedidos.
    - CLIENT: solo sus propios pedidos
    - ADMIN/PEDIDOS: todos los pedidos
    """
    return pedido_service.list_pedidos(usuario)


@router.get("/{pedido_id}")
def get_pedido(
    pedido_id: int,
    usuario: Usuario = Depends(get_current_user),
):
    return pedido_service.get_pedido(pedido_id, usuario)


@router.patch("/{pedido_id}/estado")
def cambiar_estado(
    pedido_id: int,
    data: CambioEstadoRequest,
    usuario: Usuario = Depends(get_current_user),
):
    """
    Avanza el estado de un pedido.
    - ADMIN/PEDIDOS: cualquier transición válida
    - CLIENT: solo cancelar (PENDIENTE o CONFIRMADO)
    """
    return pedido_service.cambiar_estado_pedido(
        pedido_id, data.nuevo_estado_id, usuario, data.observacion
    )


@router.get("/{pedido_id}/historial")
def get_historial(
    pedido_id: int,
    usuario: Usuario = Depends(get_current_user),
):
    """Historial completo de transiciones del pedido."""
    return pedido_service.get_historial_pedido(pedido_id, usuario)


@router.get("/{pedido_id}/estados-posibles")
def get_estados_posibles(
    pedido_id: int,
    usuario: Usuario = Depends(get_current_user),
):
    """Estados a los que se puede transicionar desde el estado actual."""
    return pedido_service.get_estados_posibles(pedido_id, usuario)
