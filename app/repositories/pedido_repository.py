from typing import Optional, List
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from app.models.pedido import Pedido
from app.models.detalle_pedido import DetallePedido
from app.models.historial_estado_pedido import HistorialEstadoPedido
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