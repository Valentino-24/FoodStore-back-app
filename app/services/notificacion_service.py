from app.core.websocket_manager import manager
from app.core.uow import UnitOfWork
from app.models.estado_pedido import EstadoPedido
from sqlmodel import select


async def notificar_cambio_estado(pedido_id: int, usuario_id: int, estado_codigo: str, observacion: str | None = None) -> None:
    """Envía notificación WebSocket a cliente + admins cuando un pedido cambia de estado."""

    data = {
        "type": "pedido_estado_update",
        "pedido_id": pedido_id,
        "estado_codigo": estado_codigo,
        "observacion": observacion,
    }

    await manager.notify_user(usuario_id, data)

    await manager.notify_admins(data)


async def notificar_nuevo_pedido(pedido_id: int, usuario_id: int, total: float) -> None:
    """Notifica a admins sobre un nuevo pedido creado."""

    data = {
        "type": "pedido_nuevo",
        "pedido_id": pedido_id,
        "usuario_id": usuario_id,
        "total": total,
    }

    await manager.notify_admins(data)
