from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.models.usuario import Usuario
from app.services import admin_service
from app.core.dependencies import require_admin
from app.schemas.admin import UsuarioAdminUpdate, UsuarioCreateAdmin, AsignarRolesRequest

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/usuarios")
def create_usuario(
    data: UsuarioCreateAdmin,
    _: Usuario = Depends(require_admin),
):

    return admin_service.create_usuario(data)

@router.get("/usuarios")
def list_usuarios(
    rol: Optional[str] = Query(None, description="Filtrar por rol"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    _: Usuario = Depends(require_admin),
):

    return admin_service.list_usuarios(rol=rol, skip=skip, limit=limit)

@router.get("/usuarios/{usuario_id}")
def get_usuario(
    usuario_id: int,
    _: Usuario = Depends(require_admin),
):

    return admin_service.get_usuario(usuario_id)

@router.put("/usuarios/{usuario_id}")
def update_usuario(
    usuario_id: int,
    data: UsuarioAdminUpdate,
    _: Usuario = Depends(require_admin),
):

    return admin_service.update_usuario(usuario_id, data)

@router.delete("/usuarios/{usuario_id}")
def delete_usuario(
    usuario_id: int,
    _: Usuario = Depends(require_admin),
):

    result = admin_service.soft_delete_usuario(usuario_id)
    return {"ok": True}

@router.post("/usuarios/{usuario_id}/roles")
def asignar_roles(
    usuario_id: int,
    data: AsignarRolesRequest,
    _: Usuario = Depends(require_admin),
):

    return admin_service.asignar_roles(usuario_id, data.roles_ids)