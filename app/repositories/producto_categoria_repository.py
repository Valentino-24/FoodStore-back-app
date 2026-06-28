from typing import Optional, List
from sqlmodel import Session, select, delete

from app.models.producto_categoria import ProductoCategoria


class ProductoCategoriaRepository:
    """Repositorio para la tabla de junction Producto-Categoria.

    No hereda de BaseRepository porque las operaciones de junction
    no deben commitear individualmente — el Unit of Work controla
    la transacción completa.
    """

    def __init__(self, session: Session):
        self.session = session

    def add_relation(
        self,
        producto_id: int,
        categoria_id: int,
        es_principal: bool = False,
    ) -> ProductoCategoria:
        rel = ProductoCategoria(
            producto_id=producto_id,
            categoria_id=categoria_id,
            es_principal=es_principal,
        )
        self.session.add(rel)
        return rel

    def remove_all_by_producto(self, producto_id: int) -> None:
        self.session.exec(
            delete(ProductoCategoria).where(
                ProductoCategoria.producto_id == producto_id
            )
        )

    def remove_all_by_categoria(self, categoria_id: int) -> None:
        self.session.exec(
            delete(ProductoCategoria).where(
                ProductoCategoria.categoria_id == categoria_id
            )
        )

    def get_by_producto(self, producto_id: int) -> List[ProductoCategoria]:
        stmt = select(ProductoCategoria).where(
            ProductoCategoria.producto_id == producto_id
        )
        return self.session.exec(stmt).all()

    def get_by_categoria(self, categoria_id: int) -> List[ProductoCategoria]:
        stmt = select(ProductoCategoria).where(
            ProductoCategoria.categoria_id == categoria_id
        )
        return self.session.exec(stmt).all()
