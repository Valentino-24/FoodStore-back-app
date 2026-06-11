from typing import Optional, List
from sqlmodel import Session, select

from app.models.categoria import Categoria
from app.models.producto_categoria import ProductoCategoria
from app.repositories.base import BaseRepository

class CategoriaRepository(BaseRepository[Categoria]):
    def __init__(self, session: Session):
        super().__init__(session, Categoria)

    def get_by_parent(self, parent_id: Optional[int], skip: int = 0, limit: int = 20) -> List[Categoria]:
        stmt = select(Categoria).where(Categoria.deleted_at.is_(None))
        if parent_id is None:
            stmt = stmt.where(Categoria.parent_id.is_(None))
        else:
            stmt = stmt.where(Categoria.parent_id == parent_id)
        stmt = stmt.offset(skip).limit(limit)
        return self.session.exec(stmt).all()

    def count_by_parent(self, parent_id: Optional[int]) -> int:
        stmt = select(Categoria).where(Categoria.deleted_at.is_(None))
        if parent_id is None:
            stmt = stmt.where(Categoria.parent_id.is_(None))
        else:
            stmt = stmt.where(Categoria.parent_id == parent_id)
        return len(self.session.exec(stmt).all())

    def tiene_productos_activos(self, categoria_id: int) -> bool:

        stmt = (
            select(ProductoCategoria)
            .where(ProductoCategoria.categoria_id == categoria_id)
        )
        return len(self.session.exec(stmt).all()) > 0