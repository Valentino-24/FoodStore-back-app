from sqlmodel import Session

from app.models.unidad_medida import UnidadMedida
from app.repositories.base import BaseRepository


class UnidadMedidaRepository(BaseRepository[UnidadMedida]):
    def __init__(self, session: Session):
        super().__init__(session, UnidadMedida)
