from typing import Optional, List
from sqlmodel import Session, select
from sqlalchemy import or_

from app.models.producto import Producto
from app.models.producto_categoria import ProductoCategoria
from app.repositories.base import BaseRepository

class ProductoRepository(BaseRepository[Producto]):
    def __init__(self, session: Session):
        super().__init__(session, Producto)

    def _apply_filters(
        self,
        stmt,
        categoria_id: Optional[int] = None,
        disponible: Optional[bool] = None,
        busqueda: Optional[str] = None,
    ):
        stmt = stmt.where(Producto.deleted_at.is_(None))

        if categoria_id is not None:
            stmt = stmt.where(
                Producto.id.in_(
                    select(ProductoCategoria.producto_id).where(
                        ProductoCategoria.categoria_id == categoria_id
                    )
                )
            )

        if disponible is not None:
            stmt = stmt.where(Producto.disponible == disponible)

        if busqueda:
            like_pattern = f"%{busqueda}%"
            stmt = stmt.where(
                or_(
                    Producto.nombre.ilike(like_pattern),
                    Producto.descripcion.ilike(like_pattern),
                )
            )

        return stmt

    def get_all_with_filters(
        self,
        categoria_id: Optional[int] = None,
        disponible: Optional[bool] = None,
        busqueda: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Producto]:
        stmt = self._apply_filters(
            select(Producto),
            categoria_id=categoria_id,
            disponible=disponible,
            busqueda=busqueda,
        )
        stmt = stmt.offset(skip).limit(limit)
        return self.session.exec(stmt).all()

    def count_with_filters(
        self,
        categoria_id: Optional[int] = None,
        disponible: Optional[bool] = None,
        busqueda: Optional[str] = None,
    ) -> int:
        stmt = self._apply_filters(
            select(Producto),
            categoria_id=categoria_id,
            disponible=disponible,
            busqueda=busqueda,
        )
        return len(self.session.exec(stmt).all())