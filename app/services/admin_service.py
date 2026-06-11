from typing import Optional, List

from fastapi import HTTPException

from app.core.security import hash_password
from app.core.uow import UnitOfWork
from app.models.usuario import Usuario
from app.models.usuario_rol import UsuarioRol
from app.models.rol import Rol

def create_usuario(data) -> dict:

    VALID_ROLES = {"ADMIN", "STOCK", "PEDIDOS", "CLIENT"}

    rol_upper = data.rol.upper() if data.rol else "CLIENT"
    if rol_upper not in VALID_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Rol inválido. Debe ser uno de: {', '.join(sorted(VALID_ROLES))}",
        )

    with UnitOfWork() as uow:
        existing = uow.usuarios.get_by_email(data.email)
        if existing:
            raise HTTPException(status_code=400, detail="El email ya está registrado")

        usuario = Usuario(
            email=data.email,
            hashed_password=hash_password(data.password),
            nombre=data.nombre,
            rol=rol_upper,
        )
        uow.usuarios.create(usuario)

        rol_obj = uow.roles.get_by_codigo(rol_upper)
        if rol_obj:
            uow.session.add(UsuarioRol(usuario_id=usuario.id, rol_id=rol_obj.id))

        uow.commit()

        return {
            "id": usuario.id,
            "email": usuario.email,
            "nombre": usuario.nombre,
            "rol": usuario.rol,
        }

def list_usuarios(
    rol: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
) -> dict:
    with UnitOfWork() as uow:
        usuarios = uow.usuarios.get_all_paginated(rol=rol, skip=skip, limit=limit)
        total = uow.usuarios.count_paginated(rol=rol)

        return {
            "items": [
                {
                    "id": u.id,
                    "email": u.email,
                    "nombre": u.nombre,
                    "rol": u.rol,
                    "deleted_at": u.deleted_at.isoformat() if u.deleted_at else None,
                }
                for u in usuarios
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        }

def get_usuario(usuario_id: int) -> dict:
    with UnitOfWork() as uow:
        usuario = uow.usuarios.get_by_id_including_deleted(usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        from sqlmodel import select
        from app.models.rol import Rol
        roles_usuario = uow.session.exec(
            select(Rol).join(UsuarioRol).where(UsuarioRol.usuario_id == usuario.id)
        ).all()

        return {
            "id": usuario.id,
            "email": usuario.email,
            "nombre": usuario.nombre,
            "rol": usuario.rol,
            "deleted_at": usuario.deleted_at.isoformat() if usuario.deleted_at else None,
            "roles": [
                {"id": r.id, "codigo": r.codigo, "nombre": r.nombre}
                for r in roles_usuario
            ],
        }

def update_usuario(usuario_id: int, data) -> dict:
    with UnitOfWork() as uow:
        usuario = uow.usuarios.get_by_id_including_deleted(usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if key == "rol":
                setattr(usuario, key, value.upper())
            else:
                setattr(usuario, key, value)

        uow.usuarios.update(usuario)

        return {
            "id": usuario.id,
            "email": usuario.email,
            "nombre": usuario.nombre,
            "rol": usuario.rol,
        }

def soft_delete_usuario(usuario_id: int) -> bool:
    with UnitOfWork() as uow:
        usuario = uow.usuarios.get_by_id(usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        uow.usuarios.soft_delete(usuario)
        return True

def asignar_roles(usuario_id: int, roles_ids: List[int]) -> dict:
    with UnitOfWork() as uow:
        usuario = uow.usuarios.get_by_id(usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        from app.models.rol import Rol
        roles = []
        for rid in roles_ids:
            rol = uow.session.get(Rol, rid)
            if not rol:
                raise HTTPException(status_code=404, detail=f"Rol con id {rid} no encontrado")
            roles.append(rol)

        from sqlmodel import delete
        uow.session.exec(
            delete(UsuarioRol).where(UsuarioRol.usuario_id == usuario_id)
        )

        for rol in roles:
            uow.session.add(UsuarioRol(usuario_id=usuario_id, rol_id=rol.id))

        if roles:
            usuario.rol = roles[0].codigo
            uow.session.add(usuario)

        uow.commit()

        return {
            "id": usuario.id,
            "email": usuario.email,
            "nombre": usuario.nombre,
            "rol": usuario.rol,
            "roles": [{"id": r.id, "codigo": r.codigo, "nombre": r.nombre} for r in roles],
        }