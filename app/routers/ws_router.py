from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query

from app.core.websocket_manager import manager
from app.core.security import decode_access_token
from app.core.uow import UnitOfWork

router = APIRouter()


@router.websocket("/ws/pedidos")
async def ws_pedidos(
    websocket: WebSocket,
    token: str = Query(...),
):
    """WebSocket para recibir notificaciones de pedidos en tiempo real.

    Conecta con ?token=<access_token>.
    - Clientes: reciben updates de sus propios pedidos.
    - Admins/PEDIDOS: reciben updates de TODOS los pedidos.
    """

    payload = decode_access_token(token)
    if payload is None:
        await websocket.close(code=4001, reason="Token inválido o expirado")
        return

    email = payload.get("sub")
    if not email:
        await websocket.close(code=4001, reason="Token inválido")
        return

    with UnitOfWork() as uow:
        usuario = uow.usuarios.get_by_email(email)
        if not usuario:
            await websocket.close(code=4001, reason="Usuario no encontrado")
            return
        user_id = usuario.id
        es_admin = usuario.rol.upper() in ("ADMIN", "PEDIDOS")

    await manager.connect(websocket, user_id, es_admin)

    try:
        while True:
            # Keep connection alive — client can send pings
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text('{"type":"pong"}')
    except WebSocketDisconnect:
        await manager.disconnect(websocket, user_id)
    except Exception:
        await manager.disconnect(websocket, user_id)
