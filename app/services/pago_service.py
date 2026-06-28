import mercadopago
from fastapi import HTTPException

from app.core.config import settings
from app.core.uow import UnitOfWork
from app.models.pago import Pago
from app.models.pedido import Pedido
from app.models.usuario import Usuario
from app.services.pedido_service import _get_estado_por_codigo, _registrar_historial


def _get_mp_client() -> mercadopago.SDK:
    if not settings.MERCADOPAGO_ACCESS_TOKEN:
        raise HTTPException(status_code=500, detail="MercadoPago no configurado")
    return mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)


def crear_preferencia(pedido_id: int, usuario: Usuario) -> dict:
    """Crea una preferencia de pago en MercadoPago y registra el pago en DB."""

    with UnitOfWork() as uow:
        pedido = uow.pedidos.get_by_id_with_relations(pedido_id)
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")

        if usuario.rol.upper() == "CLIENT" and pedido.usuario_id != usuario.id:
            raise HTTPException(status_code=403, detail="No tienes acceso a este pedido")

        # Verificar que no haya ya un pago aprobado
        pagos_existentes = uow.pagos.get_by_pedido(pedido_id)
        for p in pagos_existentes:
            if p.estado == "APROBADO":
                raise HTTPException(status_code=400, detail="El pedido ya tiene un pago aprobado")

        mp = _get_mp_client()

        preference_data = {
            "items": [
                {
                    "id": str(pedido.id),
                    "title": f"Pedido #{pedido.id} - FoodStore",
                    "quantity": 1,
                    "unit_price": float(pedido.total),
                    "currency_id": "ARS",
                }
            ],
            "external_reference": str(pedido.id),
        }

        # back_urls y auto_return solo si tenemos URL pública (no localhost)
        api_url = settings.API_URL
        frontend_url = settings.FRONTEND_URL
        if "localhost" not in api_url and "127.0.0.1" not in api_url:
            preference_data["back_urls"] = {
                "success": f"{frontend_url}/store/orders",
                "failure": f"{frontend_url}/store/orders",
                "pending": f"{frontend_url}/store/orders",
            }
            preference_data["auto_return"] = "approved"
            preference_data["notification_url"] = f"{api_url}/api/v1/pagos/webhook"

        result = mp.preference().create(preference_data)
        response = result.get("response", {})

        # Debug: log the full result when it fails
        status_code = result.get("status")
        if status_code not in (200, 201):
            import json
            error_msg = response.get("message", response.get("cause", str(result)))
            raise HTTPException(
                status_code=502,
                detail=f"Error de MercadoPago ({status_code}): {json.dumps(error_msg, ensure_ascii=False)}"
            )

        preference_id = response.get("id")
        # En desarrollo: usar sandbox para poder pagar con tarjetas de prueba
        init_point = response.get("sandbox_init_point") or response.get("init_point")

        if not preference_id:
            raise HTTPException(status_code=502, detail="Error al crear preferencia en MercadoPago")

        # Guardar en DB
        pago = Pago(
            pedido_id=pedido.id,
            monto=pedido.total,
            mp_preference_id=preference_id,
            estado="PENDIENTE",
        )
        uow.pagos.create(pago)

        return {
            "preference_id": preference_id,
            "init_point": init_point,
            "pago_id": pago.id,
            "monto": pedido.total,
        }


def procesar_webhook(data: dict) -> dict:
    """Procesa notificación de MercadoPago (IPN / Webhook)."""

    topic = data.get("topic") or data.get("type")

    # MP puede enviar tanto por query params como por body
    if not topic:
        topic = "payment" if data.get("data", {}).get("id") else None

    if topic == "payment":
        payment_id = data.get("id") or data.get("data", {}).get("id")
        if not payment_id:
            return {"mensaje": "Notificación ignorada: sin payment_id"}

        return _procesar_pago(payment_id)

    if topic in ("merchant_order", "mp-connect"):
        return {"mensaje": f"Tipo '{topic}' ignorado por ahora"}

    return {"mensaje": f"Tipo '{topic}' no soportado"}


def _procesar_pago(payment_id: int) -> dict:
    mp = _get_mp_client()
    result = mp.payment().get(payment_id)
    payment = result.get("response", {})

    if not payment:
        raise HTTPException(status_code=502, detail="No se pudo obtener información del pago")

    mp_status = payment.get("status")
    mp_status_detail = payment.get("status_detail")
    external_ref = payment.get("external_reference")
    preference_id = payment.get("preference_id")

    if not external_ref:
        return {"mensaje": "Notificación sin external_reference, ignorada"}

    try:
        pedido_id = int(external_ref)
    except (ValueError, TypeError):
        return {"mensaje": f"external_reference inválido: {external_ref}"}

    with UnitOfWork() as uow:
        pago = uow.pagos.get_by_mp_payment(payment_id)
        if not pago and preference_id:
            pago = uow.pagos.get_by_mp_preference(preference_id)

        nuevo_estado = _map_mp_status(mp_status)

        if pago:
            pago.mp_payment_id = payment_id
            pago.mp_status = mp_status
            pago.mp_status_detail = mp_status_detail
            pago.estado = nuevo_estado
            uow.pagos.update(pago)
        else:
            pago = Pago(
                pedido_id=pedido_id,
                monto=payment.get("transaction_amount", 0),
                mp_payment_id=payment_id,
                mp_preference_id=preference_id or "",
                mp_status=mp_status,
                mp_status_detail=mp_status_detail,
                estado=nuevo_estado,
            )
            uow.pagos.create(pago)

        # Pago aprobado → avanzar pedido a CONFIRMADO
        if mp_status == "approved":
            pedido = uow.pedidos.get_by_id(pedido_id)
            if pedido:
                pendiente = uow.estados_pedido.get_by_codigo("PENDIENTE")
                if pendiente and pedido.estado_actual_id == pendiente.id:
                    confirmado = _get_estado_por_codigo(uow, "CONFIRMADO")
                    pedido.estado_actual_id = confirmado.id
                    uow.pedidos.update(pedido)
                    _registrar_historial(
                        uow,
                        pedido_id=pedido.id,
                        estado_anterior_id=pendiente.id,
                        estado_nuevo_id=confirmado.id,
                        cambiado_por_id=pedido.usuario_id,
                        observacion="Pago aprobado vía MercadoPago",
                    )
                    uow.commit()

        return {
            "mensaje": "Notificación procesada",
            "payment_id": payment_id,
            "estado": nuevo_estado,
        }


def _map_mp_status(mp_status: str | None) -> str:
    mapping = {
        "approved": "APROBADO",
        "in_process": "PENDIENTE",
        "in_mediation": "PENDIENTE",
        "rejected": "RECHAZADO",
        "cancelled": "CANCELADO",
        "refunded": "CANCELADO",
        "charged_back": "RECHAZADO",
    }
    return mapping.get(mp_status or "", "PENDIENTE")
