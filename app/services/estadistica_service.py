from datetime import datetime, timezone, date
from typing import Optional

from sqlalchemy import func, cast, Date
from sqlmodel import select

from app.core.uow import UnitOfWork
from app.models.pedido import Pedido
from app.models.detalle_pedido import DetallePedido
from app.models.estado_pedido import EstadoPedido
from app.models.producto import Producto


def get_resumen() -> dict:
    """Resumen general del dashboard."""

    with UnitOfWork() as uow:
        total_productos = len(uow.productos.get_all())
        total_categorias = len(uow.categorias.get_all())
        total_ingredientes = len(uow.ingredientes.get_all())
        total_usuarios = len(uow.usuarios.get_all())
        total_pedidos = len(uow.pedidos.get_all())

        ingresos = uow.session.exec(
            select(func.coalesce(func.sum(Pedido.total), 0)).where(Pedido.deleted_at.is_(None))
        ).one()
        ingresos_totales = float(ingresos) if ingresos is not None else 0.0

        hoy_inicio = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        pedidos_hoy = uow.session.exec(
            select(func.count(Pedido.id)).where(
                Pedido.fecha_pedido >= hoy_inicio,
                Pedido.deleted_at.is_(None),
            )
        ).one()

        # Pedido promedio
        total_count = uow.session.exec(
            select(func.count(Pedido.id)).where(Pedido.deleted_at.is_(None))
        ).one()
        ticket_promedio = round(ingresos_totales / total_count, 2) if total_count > 0 else 0.0

        # Pedidos por estado
        estados = uow.session.exec(select(EstadoPedido)).all()
        pedidos_por_estado = []
        for e in estados:
            count = uow.session.exec(
                select(func.count(Pedido.id))
                .where(Pedido.estado_actual_id == e.id, Pedido.deleted_at.is_(None))
            ).one()
            pedidos_por_estado.append({
                "codigo": e.codigo,
                "nombre": e.nombre,
                "cantidad": count,
            })

        return {
            "total_productos": total_productos,
            "total_categorias": total_categorias,
            "total_ingredientes": total_ingredientes,
            "total_usuarios": total_usuarios,
            "total_pedidos": total_pedidos,
            "pedidos_hoy": pedidos_hoy,
            "ingresos_totales": round(ingresos_totales, 2),
            "ticket_promedio": ticket_promedio,
            "pedidos_por_estado": pedidos_por_estado,
        }


def get_ventas(
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    agrupar_por: str = "dia",
) -> list[dict]:
    """Ventas agrupadas por día, semana o mes."""

    with UnitOfWork() as uow:
        stmt = select(
            cast(Pedido.fecha_pedido, Date).label("fecha"),
            func.count(Pedido.id).label("cantidad"),
            func.coalesce(func.sum(Pedido.total), 0).label("ingresos"),
        ).where(Pedido.deleted_at.is_(None))

        if fecha_desde:
            stmt = stmt.where(Pedido.fecha_pedido >= fecha_desde)
        if fecha_hasta:
            stmt = stmt.where(Pedido.fecha_pedido <= datetime.combine(fecha_hasta, datetime.max.time()))

        stmt = stmt.group_by(cast(Pedido.fecha_pedido, Date)).order_by(
            cast(Pedido.fecha_pedido, Date).desc()
        )
        stmt = stmt.limit(90)  # últimos 90 días máximo

        resultados = uow.session.exec(stmt).all()

        return [
            {
                "fecha": str(row.fecha) if hasattr(row, "fecha") else str(row[0]),
                "cantidad_pedidos": row.cantidad if hasattr(row, "cantidad") else row[1],
                "ingresos": round(float(row.ingresos) if hasattr(row, "ingresos") else float(row[2]), 2),
            }
            for row in resultados
        ]


def get_productos_mas_vendidos(limite: int = 10) -> list[dict]:
    """Productos más vendidos por cantidad."""

    with UnitOfWork() as uow:
        stmt = (
            select(
                DetallePedido.producto_id,
                Producto.nombre,
                func.sum(DetallePedido.cantidad).label("total_vendido"),
                func.sum(DetallePedido.subtotal).label("total_ingresos"),
            )
            .join(Producto, DetallePedido.producto_id == Producto.id)
            .join(Pedido, DetallePedido.pedido_id == Pedido.id)
            .where(Pedido.deleted_at.is_(None))
            .group_by(DetallePedido.producto_id, Producto.nombre)
            .order_by(func.sum(DetallePedido.cantidad).desc())
            .limit(limite)
        )

        resultados = uow.session.exec(stmt).all()

        return [
            {
                "producto_id": row.producto_id if hasattr(row, "producto_id") else row[0],
                "nombre": row.nombre if hasattr(row, "nombre") else row[1],
                "total_vendido": int(row.total_vendido) if hasattr(row, "total_vendido") else int(row[2]),
                "total_ingresos": round(float(row.total_ingresos) if hasattr(row, "total_ingresos") else float(row[3]), 2),
            }
            for row in resultados
        ]


def get_pedidos_por_estado() -> list[dict]:
    """Distribución de pedidos por estado."""

    with UnitOfWork() as uow:
        estados = uow.session.exec(select(EstadoPedido)).all()
        resultado = []
        for e in estados:
            count = uow.session.exec(
                select(func.count(Pedido.id))
                .where(Pedido.estado_actual_id == e.id, Pedido.deleted_at.is_(None))
            ).one()
            resultado.append({
                "codigo": e.codigo,
                "nombre": e.nombre,
                "cantidad": count,
            })
        return resultado
