from typing import Optional, List
from datetime import datetime
from sqlmodel import Session, select, delete

from app.models.usuario_rol import UsuarioRol
from app.models.rol import Rol


class UsuarioRolRepository:
    """Repositorio para la tabla de junction Usuario-Rol.

    No hereda de BaseRepository porque las operaciones de junction
    no deben commitear individualmente — el Unit of Work controla
    la transacción completa.
    """

    def __init__(self, session: Session):
        self.session = session

    def add_role(
        self,
        usuario_id: int,
        rol_id: int,
        asignado_por_id: Optional[int] = None,
        expires_at: Optional[datetime] = None,
    ) -> UsuarioRol:
        rel = UsuarioRol(
            usuario_id=usuario_id,
            rol_id=rol_id,
            asignado_por_id=asignado_por_id,
            expires_at=expires_at,
        )
        self.session.add(rel)
        return rel

    def remove_all_roles(self, usuario_id: int) -> None:
        self.session.exec(
            delete(UsuarioRol).where(UsuarioRol.usuario_id == usuario_id)
        )

    def get_roles_by_usuario(self, usuario_id: int) -> List[Rol]:
        stmt = (
            select(Rol)
            .join(UsuarioRol, UsuarioRol.rol_id == Rol.id)
            .where(UsuarioRol.usuario_id == usuario_id)
        )
        return self.session.exec(stmt).all()

    def get_by_usuario(self, usuario_id: int) -> List[UsuarioRol]:
        stmt = select(UsuarioRol).where(UsuarioRol.usuario_id == usuario_id)
        return self.session.exec(stmt).all()
