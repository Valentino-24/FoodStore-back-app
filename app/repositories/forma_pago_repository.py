from typing import Optional, List
from sqlmodel import Session, select

from app.models.forma_pago import FormaPago
from app.repositories.base import BaseRepository


class FormaPagoRepository(BaseRepository[FormaPago]):
    def __init__(self, session: Session):
        super().__init__(session, FormaPago)

    def get_by_codigo(self, codigo: str) -> Optional[FormaPago]:
        stmt = select(FormaPago).where(FormaPago.codigo == codigo)
        return self.session.exec(stmt).first()

    def get_all_activas(self) -> List[FormaPago]:
        stmt = select(FormaPago).order_by(FormaPago.nombre)
        return self.session.exec(stmt).all()
