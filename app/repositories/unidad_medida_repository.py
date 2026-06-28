from typing import Optional

from sqlmodel import Session, select

from app.models.unidad_medida import UnidadMedida
from app.repositories.base import BaseRepository


class UnidadMedidaRepository(BaseRepository[UnidadMedida]):
    def __init__(self, session: Session):
        super().__init__(session, UnidadMedida)

    def get_by_simbolo(self, simbolo: str) -> Optional[UnidadMedida]:
        stmt = select(UnidadMedida).where(UnidadMedida.simbolo == simbolo)
        return self.session.exec(stmt).first()
