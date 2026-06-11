from typing import Optional, List
from sqlmodel import Session, select

from app.models.direccion_entrega import DireccionEntrega
from app.repositories.base import BaseRepository

class DireccionRepository(BaseRepository[DireccionEntrega]):
    def __init__(self, session: Session):
        super().__init__(session, DireccionEntrega)

    def get_by_usuario(self, usuario_id: int) -> List[DireccionEntrega]:
        stmt = (
            select(DireccionEntrega)
            .where(
                DireccionEntrega.usuario_id == usuario_id,
                DireccionEntrega.deleted_at.is_(None),
            )
            .order_by(DireccionEntrega.es_principal.desc())
        )
        return self.session.exec(stmt).all()

    def get_principal(self, usuario_id: int) -> Optional[DireccionEntrega]:
        stmt = (
            select(DireccionEntrega)
            .where(
                DireccionEntrega.usuario_id == usuario_id,
                DireccionEntrega.es_principal == True,
                DireccionEntrega.deleted_at.is_(None),
            )
        )
        return self.session.exec(stmt).first()

    def quitar_principal(self, usuario_id: int) -> None:

        stmt = (
            select(DireccionEntrega)
            .where(
                DireccionEntrega.usuario_id == usuario_id,
                DireccionEntrega.deleted_at.is_(None),
            )
        )
        direcciones = self.session.exec(stmt).all()
        for d in direcciones:
            d.es_principal = False
            self.session.add(d)