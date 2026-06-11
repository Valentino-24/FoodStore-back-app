from fastapi import HTTPException
from sqlmodel import select
from sqlalchemy.orm import selectinload

from app.core.uow import UnitOfWork
from app.models.pedido import Pedido
from app.models.detalle_pedido import DetallePedido
from app.models.historial_estado_pedido import HistorialEstadoPedido
from app.models.estado_pedido import EstadoPedido
from app.models.forma_pago import FormaPago
from app.models.producto import Producto
from app.models.direccion_entrega import DireccionEntrega
from app.models.usuario import Usuario

TRANSICIONES_VALIDAS = {
    "PENDIENTE": ["CONFIRMADO", "CANCELADO"],
    "CONFIRMADO": ["EN_PREP", "CANCELADO"],
    "EN_PREP": ["EN_CAMINO"],
    "EN_CAMINO": ["ENTREGADO"],
    "ENTREGADO": [],
    "CANCELADO": [],
}

ESTADOS_CANCELABLES_POR_CLIENTE = {"PENDIENTE", "CONFIRMADO"}

def _get_estado_por_id(uow: UnitOfWork, estado_id: int) -> EstadoPedido:
    estado = uow.session.get(EstadoPedido, estado_id)
    if not estado:
        raise HTTPException(status_code=404, detail="Estado de pedido no encontrado")
    return estado

def _get_estado_por_codigo(uow: UnitOfWork, codigo: str) -> EstadoPedido:
    estado = uow.session.exec(
        select(EstadoPedido).where(EstadoPedido.codigo == codigo)
    ).first()
    if not estado:
        raise HTTPException(status_code=404, detail=f"Estado '{codigo}' no encontrado")
    return estado

def _validar_transicion(estado_actual_codigo: str, nuevo_estado_codigo: str) -> None:
    destinos = TRANSICIONES_VALIDAS.get(estado_actual_codigo, [])
    if nuevo_estado_codigo not in destinos:
        raise HTTPException(
            status_code=400,
            detail=f"Transición inválida: {estado_actual_codigo} → {nuevo_estado_codigo}. "
                   f"Transiciones permitidas: {destinos}",
        )

def _registrar_historial(
    uow: UnitOfWork,
    pedido_id: int,
    estado_anterior_id: int | None,
    estado_nuevo_id: int,
    cambiado_por_id: int,
    observacion: str | None = None,
) -> HistorialEstadoPedido:
    historial = HistorialEstadoPedido(
        pedido_id=pedido_id,
        estado_anterior_id=estado_anterior_id,
        estado_nuevo_id=estado_nuevo_id,
        cambiado_por_id=cambiado_por_id,
        observacion=observacion,
    )
    uow.session.add(historial)
    return historial

def _build_pedido_response(uow: UnitOfWork, pedido: Pedido) -> dict:

    stmt = (
        select(Pedido)
        .where(Pedido.id == pedido.id)
        .options(
            selectinload(Pedido.detalles),
            selectinload(Pedido.estado_actual),
            selectinload(Pedido.forma_pago),
            selectinload(Pedido.direccion),
        )
    )
    pedido = uow.session.exec(stmt).first()

    historial = uow.historial_estados.get_by_pedido(pedido.id)
    historial_data = []
    for h in historial:
        hist_item = {
            "id": h.id,
            "pedido_id": h.pedido_id,
            "estado_anterior_id": h.estado_anterior_id,
            "estado_nuevo_id": h.estado_nuevo_id,
            "cambiado_por_id": h.cambiado_por_id,
            "fecha_cambio": h.fecha_cambio.isoformat() if h.fecha_cambio else None,
            "observacion": h.observacion,
        }
        if h.estado_anterior:
            hist_item["estado_anterior"] = {
                "id": h.estado_anterior.id,
                "codigo": h.estado_anterior.codigo,
                "nombre": h.estado_anterior.nombre,
                "orden": h.estado_anterior.orden,
            }
        if h.estado_nuevo:
            hist_item["estado_nuevo"] = {
                "id": h.estado_nuevo.id,
                "codigo": h.estado_nuevo.codigo,
                "nombre": h.estado_nuevo.nombre,
                "orden": h.estado_nuevo.orden,
            }
        historial_data.append(hist_item)

    return {
        "id": pedido.id,
        "usuario_id": pedido.usuario_id,
        "fecha_pedido": pedido.fecha_pedido.isoformat() if pedido.fecha_pedido else None,
        "estado_actual_id": pedido.estado_actual_id,
        "forma_pago_id": pedido.forma_pago_id,
        "direccion_entrega_id": pedido.direccion_entrega_id,
        "total": pedido.total,
        "detalles": [
            {
                "id": d.id,
                "producto_id": d.producto_id,
                "nombre_producto": d.nombre_producto,
                "precio_unitario": d.precio_unitario,
                "cantidad": d.cantidad,
                "subtotal": d.subtotal,
            }
            for d in (pedido.detalles or [])
        ],
        "estado_actual": {
            "id": pedido.estado_actual.id,
            "codigo": pedido.estado_actual.codigo,
            "nombre": pedido.estado_actual.nombre,
            "orden": pedido.estado_actual.orden,
        } if pedido.estado_actual else None,
        "forma_pago": {
            "id": pedido.forma_pago.id,
            "nombre": pedido.forma_pago.nombre,
            "codigo": pedido.forma_pago.codigo,
        } if pedido.forma_pago else None,
        "historial_estados": historial_data,
    }

def create_pedido(usuario: Usuario, data) -> dict:

    with UnitOfWork() as uow:

        fp = uow.session.get(FormaPago, data.forma_pago_id)
        if not fp:
            raise HTTPException(status_code=404, detail="Forma de pago no encontrada")

        if data.direccion_entrega_id:
            direccion = uow.session.get(DireccionEntrega, data.direccion_entrega_id)
            if not direccion or direccion.deleted_at is not None:
                raise HTTPException(status_code=404, detail="Dirección de entrega no encontrada")
            if direccion.usuario_id != usuario.id:
                raise HTTPException(status_code=403, detail="La dirección no pertenece al usuario")

        if not data.detalles:
            raise HTTPException(status_code=400, detail="El pedido debe tener al menos un detalle")

        estado_pendiente = _get_estado_por_codigo(uow, "PENDIENTE")

        total = 0.0
        detalles = []
        for det in data.detalles:
            producto = uow.productos.get_by_id(det.producto_id)
            if not producto:
                raise HTTPException(
                    status_code=404,
                    detail=f"Producto con id {det.producto_id} no encontrado",
                )
            if not producto.disponible:
                raise HTTPException(
                    status_code=400,
                    detail=f"Producto '{producto.nombre}' no está disponible",
                )
            if producto.stock_cantidad < det.cantidad:
                raise HTTPException(
                    status_code=400,
                    detail=f"Stock insuficiente para '{producto.nombre}': "
                           f"disponible {producto.stock_cantidad}, solicitado {det.cantidad}",
                )

            subtotal = producto.precio_base * det.cantidad
            total += subtotal

            detalle = DetallePedido(
                producto_id=producto.id,
                nombre_producto=producto.nombre,
                precio_unitario=producto.precio_base,
                cantidad=det.cantidad,
                subtotal=subtotal,
            )
            detalles.append(detalle)

            producto.stock_cantidad -= det.cantidad
            uow.session.add(producto)

        pedido = Pedido(
            usuario_id=usuario.id,
            estado_actual_id=estado_pendiente.id,
            forma_pago_id=data.forma_pago_id,
            direccion_entrega_id=data.direccion_entrega_id,
            total=round(total, 2),
        )
        uow.session.add(pedido)
        uow.session.flush()

        for det in detalles:
            det.pedido_id = pedido.id
            uow.session.add(det)

        _registrar_historial(
            uow,
            pedido_id=pedido.id,
            estado_anterior_id=None,
            estado_nuevo_id=estado_pendiente.id,
            cambiado_por_id=usuario.id,
            observacion="Pedido creado",
        )

        uow.commit()
        uow.session.refresh(pedido)

        return _build_pedido_response(uow, pedido)

def get_pedido(pedido_id: int, usuario: Usuario) -> dict:

    with UnitOfWork() as uow:
        pedido = uow.pedidos.get_by_id_with_relations(pedido_id)
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")

        if usuario.rol.upper() == "CLIENT" and pedido.usuario_id != usuario.id:
            raise HTTPException(status_code=403, detail="No tienes acceso a este pedido")

        return _build_pedido_response(uow, pedido)

def list_pedidos(usuario: Usuario) -> list:

    with UnitOfWork() as uow:
        if usuario.rol.upper() in ("ADMIN", "PEDIDOS"):
            pedidos = uow.pedidos.get_all_activos()
        else:
            pedidos = uow.pedidos.get_by_usuario(usuario.id)

        return [_build_pedido_response(uow, p) for p in pedidos]

def cambiar_estado_pedido(
    pedido_id: int,
    nuevo_estado_id: int,
    usuario: Usuario,
    observacion: str | None = None,
) -> dict:

    with UnitOfWork() as uow:
        pedido = uow.pedidos.get_by_id_with_relations(pedido_id)
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")

        estado_actual = _get_estado_por_id(uow, pedido.estado_actual_id)
        estado_nuevo = _get_estado_por_id(uow, nuevo_estado_id)

        _validar_transicion(estado_actual.codigo, estado_nuevo.codigo)

        if usuario.rol.upper() == "CLIENT":
            if pedido.usuario_id != usuario.id:
                raise HTTPException(status_code=403, detail="No puedes cambiar el estado de este pedido")
            if estado_nuevo.codigo != "CANCELADO":
                raise HTTPException(status_code=403, detail="Como cliente solo puedes cancelar el pedido")
            if estado_actual.codigo not in ESTADOS_CANCELABLES_POR_CLIENTE:
                raise HTTPException(
                    status_code=400,
                    detail=f"No puedes cancelar un pedido en estado '{estado_actual.codigo}'. "
                           f"Solo se puede cancelar desde: {', '.join(ESTADOS_CANCELABLES_POR_CLIENTE)}",
                )

        estado_anterior_id = pedido.estado_actual_id

        pedido.estado_actual_id = nuevo_estado_id
        uow.session.add(pedido)

        _registrar_historial(
            uow,
            pedido_id=pedido.id,
            estado_anterior_id=estado_anterior_id,
            estado_nuevo_id=nuevo_estado_id,
            cambiado_por_id=usuario.id,
            observacion=observacion,
        )

        uow.commit()

        return _build_pedido_response(uow, pedido)

def get_historial_pedido(pedido_id: int, usuario: Usuario) -> list:

    with UnitOfWork() as uow:
        pedido = uow.pedidos.get_by_id(pedido_id)
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")

        if usuario.rol.upper() == "CLIENT" and pedido.usuario_id != usuario.id:
            raise HTTPException(status_code=403, detail="No tienes acceso a este pedido")

        historial = uow.historial_estados.get_by_pedido(pedido_id)
        return [
            {
                "id": h.id,
                "pedido_id": h.pedido_id,
                "estado_anterior_id": h.estado_anterior_id,
                "estado_nuevo_id": h.estado_nuevo_id,
                "cambiado_por_id": h.cambiado_por_id,
                "fecha_cambio": h.fecha_cambio.isoformat() if h.fecha_cambio else None,
                "observacion": h.observacion,
                "estado_anterior": {
                    "id": h.estado_anterior.id,
                    "codigo": h.estado_anterior.codigo,
                    "nombre": h.estado_anterior.nombre,
                } if h.estado_anterior else None,
                "estado_nuevo": {
                    "id": h.estado_nuevo.id,
                    "codigo": h.estado_nuevo.codigo,
                    "nombre": h.estado_nuevo.nombre,
                } if h.estado_nuevo else None,
            }
            for h in historial
        ]

def get_estados_posibles(pedido_id: int, usuario: Usuario) -> list:

    with UnitOfWork() as uow:
        pedido = uow.pedidos.get_by_id(pedido_id)
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")

        if usuario.rol.upper() == "CLIENT" and pedido.usuario_id != usuario.id:
            raise HTTPException(status_code=403, detail="No tienes acceso a este pedido")

        estado_actual = uow.session.get(EstadoPedido, pedido.estado_actual_id)
        if not estado_actual:
            return []

        if usuario.rol.upper() == "CLIENT":
            if estado_actual.codigo in ESTADOS_CANCELABLES_POR_CLIENTE:
                cancelado = _get_estado_por_codigo(uow, "CANCELADO")
                return [{"id": cancelado.id, "codigo": cancelado.codigo, "nombre": cancelado.nombre}]
            return []

        codigos_destino = TRANSICIONES_VALIDAS.get(estado_actual.codigo, [])
        if not codigos_destino:
            return []

        estados = uow.session.exec(
            select(EstadoPedido).where(EstadoPedido.codigo.in_(codigos_destino))
        ).all()

        return [
            {"id": e.id, "codigo": e.codigo, "nombre": e.nombre}
            for e in sorted(estados, key=lambda x: x.orden)
        ]