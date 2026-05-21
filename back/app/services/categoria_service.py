from sqlmodel import select
from app.models.categoria import Categoria
from app.models.producto_categoria import ProductoCategoria
from app.core.uow import UnitOfWork


def create_categoria(data):
    with UnitOfWork() as uow:
        categoria = Categoria(**data.model_dump())
        uow.categorias.create(categoria)
        return categoria


def get_all_categorias():
    with UnitOfWork() as uow:
        return uow.categorias.get_all()


def get_categoria(categoria_id: int):
    with UnitOfWork() as uow:
        return uow.categorias.get_by_id(categoria_id)


def update_categoria(categoria_id: int, data):
    with UnitOfWork() as uow:
        categoria = uow.categorias.get_by_id(categoria_id)
        if not categoria:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(categoria, key, value)

        return uow.categorias.update(categoria)


def delete_categoria(categoria_id: int):
    with UnitOfWork() as uow:
        categoria = uow.categorias.get_by_id(categoria_id)
        if not categoria:
            return None

        # Eliminar relaciones con productos
        productos_asociados = uow.session.exec(
            select(ProductoCategoria).where(ProductoCategoria.categoria_id == categoria_id)
        ).all()

        for prod_cat in productos_asociados:
            uow.session.delete(prod_cat)

        # Actualizar hijos para quitar parent_id
        children = uow.session.exec(
            select(Categoria).where(Categoria.parent_id == categoria_id)
        ).all()

        for child in children:
            child.parent_id = None
            uow.session.add(child)

        uow.commit()
        uow.categorias.delete(categoria)
        return True
