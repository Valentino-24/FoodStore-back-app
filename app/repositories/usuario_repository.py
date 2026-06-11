from typing import Optional, List
from sqlmodel import Session, select

from app.models.usuario import Usuario
from app.repositories.base import BaseRepository

class UsuarioRepository(BaseRepository[Usuario]):
    def __init__(self, session: Session):
        super().__init__(session, Usuario)

    def get_by_email(self, email: str) -> Usuario | None:
        return self.session.exec(
            select(Usuario).where(Usuario.email == email)
        ).first()

    def get_all_paginated(
        self,
        rol: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Usuario]:
        stmt = select(Usuario).where(Usuario.deleted_at.is_(None))
        if rol:
            stmt = stmt.where(Usuario.rol == rol.upper())
        stmt = stmt.offset(skip).limit(limit).order_by(Usuario.id)
        return self.session.exec(stmt).all()

    def count_paginated(self, rol: Optional[str] = None) -> int:
        stmt = select(Usuario).where(Usuario.deleted_at.is_(None))
        if rol:
            stmt = stmt.where(Usuario.rol == rol.upper())
        return len(self.session.exec(stmt).all())