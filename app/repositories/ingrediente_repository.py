from sqlmodel import Session
from app.models.ingrediente import Ingrediente
from app.repositories.base import BaseRepository

class IngredienteRepository(BaseRepository[Ingrediente]):
    def __init__(self, session: Session):
        super().__init__(session, Ingrediente)