from typing import Optional, List
from sqlmodel import Session, select, delete

from app.models.producto_ingrediente import ProductoIngrediente


class ProductoIngredienteRepository:
    """Repositorio para la tabla de junction Producto-Ingrediente.

    No hereda de BaseRepository porque las operaciones de junction
    no deben commitear individualmente — el Unit of Work controla
    la transacción completa.
    """

    def __init__(self, session: Session):
        self.session = session

    def add_relation(
        self,
        producto_id: int,
        ingrediente_id: int,
        es_removible: bool = True,
        cantidad: Optional[float] = None,
        unidad_medida_id: Optional[int] = None,
    ) -> ProductoIngrediente:
        rel = ProductoIngrediente(
            producto_id=producto_id,
            ingrediente_id=ingrediente_id,
            es_removible=es_removible,
            cantidad=cantidad,
            unidad_medida_id=unidad_medida_id,
        )
        self.session.add(rel)
        return rel

    def remove_all_by_producto(self, producto_id: int) -> None:
        self.session.exec(
            delete(ProductoIngrediente).where(
                ProductoIngrediente.producto_id == producto_id
            )
        )

    def remove_relation(self, producto_id: int, ingrediente_id: int) -> None:
        self.session.exec(
            delete(ProductoIngrediente).where(
                ProductoIngrediente.producto_id == producto_id,
                ProductoIngrediente.ingrediente_id == ingrediente_id,
            )
        )

    def get_by_producto(self, producto_id: int) -> List[ProductoIngrediente]:
        stmt = select(ProductoIngrediente).where(
            ProductoIngrediente.producto_id == producto_id
        )
        return self.session.exec(stmt).all()

    def get_by_ids(
        self, producto_id: int, ingrediente_id: int
    ) -> Optional[ProductoIngrediente]:
        stmt = select(ProductoIngrediente).where(
            ProductoIngrediente.producto_id == producto_id,
            ProductoIngrediente.ingrediente_id == ingrediente_id,
        )
        return self.session.exec(stmt).first()

    def update_relation(
        self,
        producto_id: int,
        ingrediente_id: int,
        **kwargs,
    ) -> Optional[ProductoIngrediente]:
        rel = self.get_by_ids(producto_id, ingrediente_id)
        if rel is None:
            return None
        for key, value in kwargs.items():
            if hasattr(rel, key):
                setattr(rel, key, value)
        self.session.add(rel)
        return rel
