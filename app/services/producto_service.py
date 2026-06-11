from typing import Optional

from fastapi import HTTPException
from sqlmodel import select, delete as sqlmodel_delete

from app.models.producto import Producto
from app.models.producto_categoria import ProductoCategoria
from app.models.producto_ingrediente import ProductoIngrediente
from app.models.categoria import Categoria
from app.models.ingrediente import Ingrediente
from app.core.uow import UnitOfWork

def delete_producto(producto_id: int):
    with UnitOfWork() as uow:
        producto = uow.productos.get_by_id(producto_id)

        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        uow.session.exec(
            sqlmodel_delete(ProductoCategoria).where(
                ProductoCategoria.producto_id == producto_id
            )
        )

        uow.session.exec(
            sqlmodel_delete(ProductoIngrediente).where(
                ProductoIngrediente.producto_id == producto_id
            )
        )

        uow.productos.soft_delete(producto)

        return {"ok": True}

def update_producto(producto_id: int, data):
    with UnitOfWork() as uow:
        producto = uow.productos.get_by_id(producto_id)

        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        if data.nombre is not None:
            producto.nombre = data.nombre

        if data.descripcion is not None:
            producto.descripcion = data.descripcion

        if data.precio_base is not None:
            producto.precio_base = data.precio_base

        if data.stock_cantidad is not None:
            producto.stock_cantidad = data.stock_cantidad

        if data.disponible is not None:
            producto.disponible = data.disponible

        if data.imagenes is not None:
            producto.imagenes = data.imagenes

        uow.session.exec(
            sqlmodel_delete(ProductoCategoria).where(
                ProductoCategoria.producto_id == producto_id
            )
        )

        uow.session.exec(
            sqlmodel_delete(ProductoIngrediente).where(
                ProductoIngrediente.producto_id == producto_id
            )
        )

        if not data.categorias:
            raise HTTPException(status_code=400, detail="Debe tener al menos una categoría")

        principales = [c for c in data.categorias if c.es_principal]

        if len(principales) != 1:
            raise HTTPException(
                status_code=400,
                detail="Debe haber una sola categoría principal"
            )

        for cat in data.categorias:
            categoria = uow.categorias.get_by_id(cat.id)
            if not categoria:
                raise HTTPException(
                    status_code=400,
                    detail=f"La categoria con id {cat.id} no existe"
                )

            uow.session.add(ProductoCategoria(
                producto_id=producto.id,
                categoria_id=cat.id,
                es_principal=cat.es_principal
            ))

        for ing_id in data.ingredientes_ids:
            ingrediente = uow.ingredientes.get_by_id(ing_id)
            if not ingrediente:
                raise HTTPException(
                    status_code=400,
                    detail=f"El ingrediente con id {ing_id} no existe"
                )

            uow.session.add(ProductoIngrediente(
                producto_id=producto.id,
                ingrediente_id=ing_id
            ))

        uow.productos.update(producto)

        return build_producto_response(uow, producto)

def build_producto_response(uow: UnitOfWork, producto: Producto):
    categorias_rel = uow.session.exec(
        select(ProductoCategoria).where(ProductoCategoria.producto_id == producto.id)
    ).all()

    categorias = []
    for rel in categorias_rel:
        cat = uow.categorias.get_by_id(rel.categoria_id)
        if cat:
            categorias.append({
                "id": cat.id,
                "nombre": cat.nombre,
                "es_principal": rel.es_principal
            })

    ingredientes_rel = uow.session.exec(
        select(ProductoIngrediente).where(ProductoIngrediente.producto_id == producto.id)
    ).all()

    ingredientes = []
    for rel in ingredientes_rel:
        ing = uow.ingredientes.get_by_id(rel.ingrediente_id)
        if ing:
            ingredientes.append({
                "id": ing.id,
                "nombre": ing.nombre
            })

    return {
        "id": producto.id,
        "nombre": producto.nombre,
        "descripcion": producto.descripcion,
        "precio_base": producto.precio_base,
        "imagenes": producto.imagenes,
        "stock_cantidad": producto.stock_cantidad,
        "disponible": producto.disponible,
        "categorias": categorias,
        "ingredientes": ingredientes
    }

def create_producto(data):
    with UnitOfWork() as uow:
        for ing_id in data.ingredientes_ids:
            ingrediente = uow.ingredientes.get_by_id(ing_id)
            if not ingrediente:
                raise HTTPException(
                    status_code=400,
                    detail=f"El ingrediente con id {ing_id} no existe"
                )

        if not data.categorias:
            raise HTTPException(status_code=400, detail="Debe tener al menos una categoría")

        principales = [c for c in data.categorias if c.es_principal]

        if len(principales) != 1:
            raise HTTPException(
                status_code=400,
                detail="Debe haber una sola categoría principal"
            )

        producto = Producto(
            nombre=data.nombre,
            descripcion=data.descripcion,
            precio_base=data.precio_base,
            imagenes=data.imagenes,
            stock_cantidad=data.stock_cantidad,
            disponible=data.disponible
        )

        uow.productos.create(producto)

        for cat in data.categorias:
            categoria = uow.categorias.get_by_id(cat.id)
            if not categoria:
                raise HTTPException(
                    status_code=400,
                    detail=f"La categoria con id {cat.id} no existe"
                )

            uow.session.add(ProductoCategoria(
                producto_id=producto.id,
                categoria_id=cat.id,
                es_principal=cat.es_principal
            ))

        for ing_id in data.ingredientes_ids:
            uow.session.add(ProductoIngrediente(
                producto_id=producto.id,
                ingrediente_id=ing_id
            ))

        uow.commit()

        return build_producto_response(uow, producto)

def get_productos():

    with UnitOfWork() as uow:
        productos = uow.productos.get_all()
        return [build_producto_response(uow, p) for p in productos]

def get_productos_publicos(
    categoria_id: Optional[int] = None,
    disponible: Optional[bool] = None,
    busqueda: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
) -> dict:

    with UnitOfWork() as uow:
        items = uow.productos.get_all_with_filters(
            categoria_id=categoria_id,
            disponible=disponible,
            busqueda=busqueda,
            skip=skip,
            limit=limit,
        )
        total = uow.productos.count_with_filters(
            categoria_id=categoria_id,
            disponible=disponible,
            busqueda=busqueda,
        )
        return {
            "items": [build_producto_response(uow, p) for p in items],
            "total": total,
            "skip": skip,
            "limit": limit,
        }

def get_producto(producto_id: int):
    with UnitOfWork() as uow:
        producto = uow.productos.get_by_id(producto_id)
        if not producto:
            return None
        return build_producto_response(uow, producto)

def toggle_disponibilidad(producto_id: int, disponible: bool) -> dict:

    with UnitOfWork() as uow:
        producto = uow.productos.get_by_id(producto_id)
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        producto.disponible = disponible
        uow.productos.update(producto)

        return build_producto_response(uow, producto)