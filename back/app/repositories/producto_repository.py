from sqlmodel import Session, select
from app.models.producto import Producto
from app.repositories.base import BaseRepository


class ProductoRepository(BaseRepository[Producto]):
    def __init__(self, session: Session):
        super().__init__(session, Producto)

    def get_all_with_relations(self) -> list[Producto]:
        """Obtiene todos los productos (sin eagerly load relaciones)."""
        return self.session.exec(select(Producto)).all()
