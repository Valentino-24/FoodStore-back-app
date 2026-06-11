from fastapi import HTTPException

from app.core.uow import UnitOfWork
from app.models.direccion_entrega import DireccionEntrega
from app.models.usuario import Usuario

def create_direccion(usuario: Usuario, data) -> DireccionEntrega:
    with UnitOfWork() as uow:

        if data.es_principal:
            uow.direcciones.quitar_principal(usuario.id)

        direccion = DireccionEntrega(
            usuario_id=usuario.id,
            alias=data.alias,
            direccion=data.direccion,
            ciudad=data.ciudad,
            codigo_postal=data.codigo_postal,
            es_principal=data.es_principal,
        )
        uow.direcciones.create(direccion)
        return direccion

def list_direcciones(usuario: Usuario) -> list[DireccionEntrega]:
    with UnitOfWork() as uow:
        return uow.direcciones.get_by_usuario(usuario.id)

def get_direccion(direccion_id: int, usuario: Usuario) -> DireccionEntrega:
    with UnitOfWork() as uow:
        direccion = uow.direcciones.get_by_id(direccion_id)
        if not direccion:
            raise HTTPException(status_code=404, detail="Dirección no encontrada")
        if direccion.usuario_id != usuario.id:
            raise HTTPException(status_code=403, detail="Esta dirección no te pertenece")
        return direccion

def update_direccion(direccion_id: int, usuario: Usuario, data) -> DireccionEntrega:
    with UnitOfWork() as uow:
        direccion = uow.direcciones.get_by_id(direccion_id)
        if not direccion:
            raise HTTPException(status_code=404, detail="Dirección no encontrada")
        if direccion.usuario_id != usuario.id:
            raise HTTPException(status_code=403, detail="Esta dirección no te pertenece")

        update_data = data.model_dump(exclude_unset=True)

        if update_data.get("es_principal"):
            uow.direcciones.quitar_principal(usuario.id)

        for key, value in update_data.items():
            setattr(direccion, key, value)

        uow.direcciones.update(direccion)
        return direccion

def delete_direccion(direccion_id: int, usuario: Usuario) -> bool:
    with UnitOfWork() as uow:
        direccion = uow.direcciones.get_by_id(direccion_id)
        if not direccion:
            raise HTTPException(status_code=404, detail="Dirección no encontrada")
        if direccion.usuario_id != usuario.id:
            raise HTTPException(status_code=403, detail="Esta dirección no te pertenece")

        uow.direcciones.soft_delete(direccion)
        return True

def marcar_principal(direccion_id: int, usuario: Usuario) -> DireccionEntrega:
    with UnitOfWork() as uow:
        direccion = uow.direcciones.get_by_id(direccion_id)
        if not direccion:
            raise HTTPException(status_code=404, detail="Dirección no encontrada")
        if direccion.usuario_id != usuario.id:
            raise HTTPException(status_code=403, detail="Esta dirección no te pertenece")

        uow.direcciones.quitar_principal(usuario.id)
        direccion.es_principal = True
        uow.direcciones.update(direccion)
        return direccion