from datetime import datetime, timezone

from sqlalchemy import func
from sqlmodel import select

from app.core.uow import UnitOfWork
from app.models.pedido import Pedido
from app.models.estado_pedido import EstadoPedido


def get_dashboard_stats() -> dict:
    with UnitOfWork() as uow:
        # ─── Counts ─────────────────────────────────────────────
        total_productos = len(uow.productos.get_all())
        total_categorias = len(uow.categorias.get_all())
        total_ingredientes = len(uow.ingredientes.get_all())
        total_pedidos = len(uow.pedidos.get_all())

        # ─── Ingresos totales (suma del total de todos los pedidos activos) ──
        result = uow.session.exec(
            select(func.coalesce(func.sum(Pedido.total), 0)).where(
                Pedido.deleted_at.is_(None)
            )
        ).one()
        ingresos_totales = float(result) if result is not None else 0.0

        # ─── Pedidos por estado ──────────────────────────────────
        estados = uow.session.exec(select(EstadoPedido)).all()
        estado_map = {e.id: {"codigo": e.codigo, "nombre": e.nombre} for e in estados}

        pedidos_por_estado = []
        for estado in estados:
            count = uow.session.exec(
                select(func.count(Pedido.id))
                .where(Pedido.estado_actual_id == estado.id, Pedido.deleted_at.is_(None))
            ).one()
            pedidos_por_estado.append({
                "codigo": estado.codigo,
                "nombre": estado.nombre,
                "cantidad": count,
            })

        # ─── Pedidos recientes (últimos 5) ──────────────────────
        pedidos_recientes = uow.session.exec(
            select(Pedido)
            .where(Pedido.deleted_at.is_(None))
            .order_by(Pedido.fecha_pedido.desc())
            .limit(5)
        ).all()

        recientes = []
        for p in pedidos_recientes:
            estado_info = estado_map.get(p.estado_actual_id, {})
            recientes.append({
                "id": p.id,
                "total": p.total,
                "fecha": p.fecha_pedido.isoformat() if p.fecha_pedido else None,
                "estado_codigo": estado_info.get("codigo", ""),
                "estado_nombre": estado_info.get("nombre", ""),
            })

        # ─── Pedidos de hoy ─────────────────────────────────────
        hoy_inicio = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        pedidos_hoy = uow.session.exec(
            select(func.count(Pedido.id))
            .where(
                Pedido.fecha_pedido >= hoy_inicio,
                Pedido.deleted_at.is_(None),
            )
        ).one()

        return {
            "total_productos": total_productos,
            "total_categorias": total_categorias,
            "total_ingredientes": total_ingredientes,
            "total_pedidos": total_pedidos,
            "pedidos_hoy": pedidos_hoy,
            "ingresos_totales": round(ingresos_totales, 2),
            "pedidos_por_estado": pedidos_por_estado,
            "pedidos_recientes": recientes,
        }
