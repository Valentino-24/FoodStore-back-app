from fastapi import APIRouter, Depends, Request

from app.models.usuario import Usuario
from app.services import pago_service
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/pagos", tags=["Pagos"])


@router.post("/preferencia")
def crear_preferencia(
    pedido_id: int,
    usuario: Usuario = Depends(get_current_user),
):
    return pago_service.crear_preferencia(pedido_id, usuario)


@router.post("/webhook")
async def recibir_webhook(request: Request):
    """Endpoint para notificaciones de MercadoPago (IPN/Webhook)."""

    # MP puede enviar JSON body o form data
    try:
        data = await request.json()
    except Exception:
        data = dict(await request.form())

    # Query params también pueden traer datos
    query = dict(request.query_params)
    data.update(query)

    return pago_service.procesar_webhook(data)
