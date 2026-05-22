from typing import TypeVar, Generic, Optional, List
from datetime import datetime, timezone
from sqlmodel import Session, SQLModel, select
from sqlalchemy import Column, DateTime

ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseRepository(Generic[ModelType]):
    """Repositorio base genérico con CRUD base y soft delete."""

    def __init__(self, session: Session, model: type[ModelType]):
        self.session = session
        self.model = model

    def create(self, entity: ModelType) -> ModelType:
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def get_by_id(self, entity_id: int) -> Optional[ModelType]:
        """Obtiene por ID (excluye soft-deleted si el modelo soporta deleted_at)."""
        entity = self.session.get(self.model, entity_id)
        if entity is None:
            return None
        # Si tiene deleted_at, filtrar
        if hasattr(entity, "deleted_at") and entity.deleted_at is not None:
            return None
        return entity

    def get_by_id_including_deleted(self, entity_id: int) -> Optional[ModelType]:
        """Obtiene por ID incluyendo soft-deleted."""
        return self.session.get(self.model, entity_id)

    def get_all(self) -> List[ModelType]:
        """Obtiene todos los activos (excluye soft-deleted si aplica)."""
        stmt = select(self.model)
        if hasattr(self.model, "deleted_at"):
            stmt = stmt.where(self.model.deleted_at.is_(None))
        return self.session.exec(stmt).all()

    def get_all_including_deleted(self) -> List[ModelType]:
        return self.session.exec(select(self.model)).all()

    def update(self, entity: ModelType) -> ModelType:
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def delete(self, entity: ModelType) -> None:
        """Hard delete — solo para casos específicos."""
        self.session.delete(entity)
        self.session.commit()

    def soft_delete(self, entity: ModelType) -> ModelType:
        """Soft delete: marca deleted_at sin borrar el registro."""
        if hasattr(entity, "deleted_at"):
            entity.deleted_at = datetime.now(timezone.utc)
            self.session.add(entity)
            self.session.commit()
            self.session.refresh(entity)
            return entity
        # Si el modelo no tiene deleted_at, hace hard delete
        self.delete(entity)
        return entity
