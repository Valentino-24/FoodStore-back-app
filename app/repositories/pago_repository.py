from typing import Optional
from sqlmodel import Session, select
from app.models.pago import Pago
from app.repositories.base import BaseRepository


class PagoRepository(BaseRepository[Pago]):
    def __init__(self, session: Session):
        super().__init__(session, Pago)

    def get_by_pedido(self, pedido_id: int) -> list[Pago]:
        stmt = select(Pago).where(Pago.pedido_id == pedido_id).order_by(Pago.created_at.desc())
        return self.session.exec(stmt).all()

    def get_by_mp_preference(self, preference_id: str) -> Optional[Pago]:
        stmt = select(Pago).where(Pago.mp_preference_id == preference_id)
        return self.session.exec(stmt).first()

    def get_by_mp_payment(self, payment_id: int) -> Optional[Pago]:
        stmt = select(Pago).where(Pago.mp_payment_id == payment_id)
        return self.session.exec(stmt).first()
