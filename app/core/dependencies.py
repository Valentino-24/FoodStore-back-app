from fastapi import Depends, HTTPException, Request
from typing import List, Optional

from app.core.security import decode_access_token
from app.core.uow import UnitOfWork
from app.models.usuario import Usuario

def get_current_user(request: Request) -> Usuario:

    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="No autenticado")

    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Token inválido")

    with UnitOfWork() as uow:
        usuario = uow.usuarios.get_by_email(email)
        if not usuario:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        return usuario

class RoleChecker:

    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = [r.upper() for r in allowed_roles]

    def __call__(self, usuario: Usuario = Depends(get_current_user)) -> Usuario:
        if usuario.rol.upper() not in self.allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Acceso denegado. Roles requeridos: {', '.join(self.allowed_roles)}",
            )
        return usuario

require_admin = RoleChecker(["ADMIN"])
require_admin_or_stock = RoleChecker(["ADMIN", "STOCK"])
require_admin_or_pedidos = RoleChecker(["ADMIN", "PEDIDOS"])
require_admin_or_cliente = RoleChecker(["ADMIN", "CLIENT"])
require_any = RoleChecker(["ADMIN", "STOCK", "PEDIDOS", "CLIENT"])