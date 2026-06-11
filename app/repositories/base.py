from typing import TypeVar, Generic, Optional, List
from datetime import datetime, timezone
from sqlmodel import Session, SQLModel, select
from sqlalchemy import Column, DateTime

ModelType = TypeVar("ModelType", bound=SQLModel)

class BaseRepository(Generic[ModelType]):

    def __init__(self, session: Session, model: type[ModelType]):
        self.session = session
        self.model = model

    def create(self, entity: ModelType) -> ModelType:
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def get_by_id(self, entity_id: int) -> Optional[ModelType]:

        entity = self.session.get(self.model, entity_id)
        if entity is None:
            return None

        if hasattr(entity, "deleted_at") and entity.deleted_at is not None:
            return None
        return entity

    def get_by_id_including_deleted(self, entity_id: int) -> Optional[ModelType]:

        return self.session.get(self.model, entity_id)

    def get_all(self) -> List[ModelType]:

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

        self.session.delete(entity)
        self.session.commit()

    def soft_delete(self, entity: ModelType) -> ModelType:

        if hasattr(entity, "deleted_at"):
            entity.deleted_at = datetime.now(timezone.utc)
            self.session.add(entity)
            self.session.commit()
            self.session.refresh(entity)
            return entity

        self.delete(entity)
        return entity