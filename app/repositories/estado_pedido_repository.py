from typing import Optional, List
from sqlmodel import Session, select

from app.models.estado_pedido import EstadoPedido
from app.repositories.base import BaseRepository


class EstadoPedidoRepository(BaseRepository[EstadoPedido]):
    def __init__(self, session: Session):
        super().__init__(session, EstadoPedido)

    def get_by_codigo(self, codigo: str) -> Optional[EstadoPedido]:
        stmt = select(EstadoPedido).where(EstadoPedido.codigo == codigo)
        return self.session.exec(stmt).first()

    def get_all_ordenados(self) -> List[EstadoPedido]:
        stmt = select(EstadoPedido).order_by(EstadoPedido.orden)
        return self.session.exec(stmt).all()

    def get_by_codigos(self, codigos: List[str]) -> List[EstadoPedido]:
        stmt = select(EstadoPedido).where(EstadoPedido.codigo.in_(codigos))
        return self.session.exec(stmt).all()
