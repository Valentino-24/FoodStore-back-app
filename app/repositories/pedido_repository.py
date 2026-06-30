from typing import Optional, List
from datetime import date, datetime, timezone

from sqlmodel import Session, select
from sqlalchemy import func
from sqlalchemy.orm import selectinload

from app.models.pedido import Pedido
from app.models.detalle_pedido import DetallePedido
from app.models.historial_estado_pedido import HistorialEstadoPedido
from app.models.estado_pedido import EstadoPedido
from app.models.producto import Producto
from app.models.forma_pago import FormaPago
from app.models.pago import Pago
from app.repositories.base import BaseRepository

class PedidoRepository(BaseRepository[Pedido]):
    def __init__(self, session: Session):
        super().__init__(session, Pedido)

    def get_by_id_with_relations(self, pedido_id: int) -> Optional[Pedido]:
        stmt = (
            select(Pedido)
            .where(Pedido.id == pedido_id, Pedido.deleted_at.is_(None))
            .options(
                selectinload(Pedido.detalles),
                selectinload(Pedido.estado_actual),
                selectinload(Pedido.forma_pago),
                selectinload(Pedido.direccion),
                selectinload(Pedido.historial_estados),
            )
        )
        return self.session.exec(stmt).first()

    def get_by_usuario(self, usuario_id: int) -> List[Pedido]:
        stmt = (
            select(Pedido)
            .where(Pedido.usuario_id == usuario_id, Pedido.deleted_at.is_(None))
            .order_by(Pedido.fecha_pedido.desc())
        )
        return self.session.exec(stmt).all()

    def get_all_activos(self) -> List[Pedido]:
        stmt = (
            select(Pedido)
            .where(Pedido.deleted_at.is_(None))
            .order_by(Pedido.fecha_pedido.desc())
        )
        return self.session.exec(stmt).all()

    def count_by_estado(self, estado_id: int) -> int:
        """Cuenta pedidos activos en un estado específico, excluyendo CANCELADO."""
        stmt = (
            select(func.count(Pedido.id))
            .join(EstadoPedido, Pedido.estado_actual_id == EstadoPedido.id)
            .where(
                Pedido.estado_actual_id == estado_id,
                EstadoPedido.codigo != "CANCELADO",
                Pedido.deleted_at.is_(None),
            )
        )
        return self.session.exec(stmt).one()

    def count_pedidos_hoy(self) -> int:
        """Cuenta pedidos creados hoy (excluye CANCELADO)."""
        hoy_inicio = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        stmt = (
            select(func.count(Pedido.id))
            .join(EstadoPedido, Pedido.estado_actual_id == EstadoPedido.id)
            .where(
                Pedido.fecha_pedido >= hoy_inicio,
                EstadoPedido.codigo != "CANCELADO",
                Pedido.deleted_at.is_(None),
            )
        )
        return self.session.exec(stmt).one()

    def get_ingresos_totales(
        self, desde: Optional[date] = None, hasta: Optional[date] = None
    ) -> float:
        """Suma total de pedidos (excluye CANCELADO), opcionalmente en rango de fechas."""
        stmt = (
            select(func.coalesce(func.sum(Pedido.total), 0))
            .join(EstadoPedido, Pedido.estado_actual_id == EstadoPedido.id)
            .where(
                EstadoPedido.codigo != "CANCELADO",
                Pedido.deleted_at.is_(None),
            )
        )
        if desde:
            stmt = stmt.where(func.date(Pedido.fecha_pedido) >= desde)
        if hasta:
            stmt = stmt.where(func.date(Pedido.fecha_pedido) <= hasta)
        result = self.session.exec(stmt).one()
        return float(result) if result is not None else 0.0

    def get_ventas_agrupadas(
        self, desde: date, hasta: date, agrupacion: str
    ) -> List[dict]:
        """Ventas agrupadas por día/semana/mes usando DATE_TRUNC de PostgreSQL.
        Retorna lista de {periodo: date, total_ventas: Decimal, cantidad_pedidos: int}."""
        trunc = func.date_trunc(agrupacion, Pedido.fecha_pedido)
        stmt = (
            select(
                trunc.label("periodo"),
                func.sum(Pedido.total).label("total_ventas"),
                func.count(Pedido.id).label("cantidad_pedidos"),
            )
            .join(EstadoPedido, Pedido.estado_actual_id == EstadoPedido.id)
            .where(
                EstadoPedido.codigo != "CANCELADO",
                Pedido.deleted_at.is_(None),
            )
        )
        if desde:
            stmt = stmt.where(func.date(Pedido.fecha_pedido) >= desde)
        if hasta:
            stmt = stmt.where(func.date(Pedido.fecha_pedido) <= hasta)
        stmt = stmt.group_by(trunc).order_by(trunc)
        rows = self.session.exec(stmt).all()
        return [
            {
                "periodo": row.periodo,
                "total_ventas": row.total_ventas,
                "cantidad_pedidos": row.cantidad_pedidos,
            }
            for row in rows
        ]

    def get_productos_mas_vendidos(self, limit: int = 10) -> List[dict]:
        """Top productos por ingresos usando subtotal_snap de DetallePedido.
        Retorna {producto_id: int, nombre: str, total_vendido: int, total_ingresos: Decimal}."""
        stmt = (
            select(
                Producto.id.label("producto_id"),
                Producto.nombre.label("nombre"),
                func.sum(DetallePedido.cantidad).label("total_vendido"),
                func.sum(DetallePedido.subtotal_snap).label("total_ingresos"),
            )
            .join(Producto, DetallePedido.producto_id == Producto.id)
            .join(Pedido, DetallePedido.pedido_id == Pedido.id)
            .join(EstadoPedido, Pedido.estado_actual_id == EstadoPedido.id)
            .where(
                EstadoPedido.codigo != "CANCELADO",
                Pedido.deleted_at.is_(None),
            )
            .group_by(Producto.id, Producto.nombre)
            .order_by(func.sum(DetallePedido.subtotal_snap).desc())
            .limit(limit)
        )
        rows = self.session.exec(stmt).all()
        return [
            {
                "producto_id": row.producto_id,
                "nombre": row.nombre,
                "total_vendido": int(row.total_vendido),
                "total_ingresos": row.total_ingresos,
            }
            for row in rows
        ]

    def get_ingresos_por_forma_pago(
        self, desde: date, hasta: date
    ) -> List[dict]:
        """Ingresos agrupados por forma de pago, solo pagos approved.
        Retorna {forma_pago: str, total: Decimal}."""
        stmt = (
            select(
                FormaPago.nombre.label("forma_pago"),
                func.sum(Pedido.total).label("total"),
            )
            .join(FormaPago, Pedido.forma_pago_id == FormaPago.id)
            .join(EstadoPedido, Pedido.estado_actual_id == EstadoPedido.id)
            .join(Pago, Pago.pedido_id == Pedido.id)
            .where(
                EstadoPedido.codigo != "CANCELADO",
                Pedido.deleted_at.is_(None),
                Pago.estado == "APROBADO",
            )
        )
        if desde:
            stmt = stmt.where(func.date(Pedido.fecha_pedido) >= desde)
        if hasta:
            stmt = stmt.where(func.date(Pedido.fecha_pedido) <= hasta)
        stmt = stmt.group_by(FormaPago.nombre)
        rows = self.session.exec(stmt).all()
        return [
            {
                "forma_pago": row.forma_pago,
                "total": row.total,
            }
            for row in rows
        ]

    def get_recientes(self, limit: int = 5) -> List[Pedido]:
        """Pedidos más recientes con eager load de relaciones."""
        stmt = (
            select(Pedido)
            .join(EstadoPedido, Pedido.estado_actual_id == EstadoPedido.id)
            .where(
                EstadoPedido.codigo != "CANCELADO",
                Pedido.deleted_at.is_(None),
            )
            .options(
                selectinload(Pedido.estado_actual),
                selectinload(Pedido.forma_pago),
                selectinload(Pedido.detalles),
            )
            .order_by(Pedido.fecha_pedido.desc())
            .limit(limit)
        )
        return self.session.exec(stmt).all()

    def get_by_usuario_paginated(
        self, usuario_id: int, offset: int, limit: int
    ) -> tuple[List[Pedido], int]:
        """Pedidos de un usuario con paginación. Retorna (pedidos, total_count)."""
        base_stmt = select(Pedido).where(
            Pedido.usuario_id == usuario_id,
            Pedido.deleted_at.is_(None),
        )
        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total_count = self.session.exec(count_stmt).one()

        stmt = (
            base_stmt
            .order_by(Pedido.fecha_pedido.desc())
            .offset(offset)
            .limit(limit)
        )
        pedidos = self.session.exec(stmt).all()
        return pedidos, total_count

    def count_all_activos(self) -> int:
        """Cuenta total de pedidos activos (excluye CANCELADO y soft-deleted)."""
        stmt = (
            select(func.count(Pedido.id))
            .join(EstadoPedido, Pedido.estado_actual_id == EstadoPedido.id)
            .where(
                EstadoPedido.codigo != "CANCELADO",
                Pedido.deleted_at.is_(None),
            )
        )
        return self.session.exec(stmt).one()


class DetallePedidoRepository(BaseRepository[DetallePedido]):
    def __init__(self, session: Session):
        super().__init__(session, DetallePedido)

class HistorialEstadoPedidoRepository(BaseRepository[HistorialEstadoPedido]):
    def __init__(self, session: Session):
        super().__init__(session, HistorialEstadoPedido)

    def get_by_pedido(self, pedido_id: int) -> List[HistorialEstadoPedido]:
        stmt = (
            select(HistorialEstadoPedido)
            .where(HistorialEstadoPedido.pedido_id == pedido_id)
            .order_by(HistorialEstadoPedido.fecha_cambio.asc())
            .options(
                selectinload(HistorialEstadoPedido.estado_anterior),
                selectinload(HistorialEstadoPedido.estado_nuevo),
            )
        )
        return self.session.exec(stmt).all()