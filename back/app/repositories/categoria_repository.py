from sqlmodel import Session
from app.models.categoria import Categoria
from app.repositories.base import BaseRepository


class CategoriaRepository(BaseRepository[Categoria]):
    def __init__(self, session: Session):
        super().__init__(session, Categoria)
