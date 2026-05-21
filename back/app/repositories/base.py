from typing import TypeVar, Generic, Optional, List
from sqlmodel import Session, SQLModel, select

ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseRepository(Generic[ModelType]):
    """Repositorio base genérico con operaciones CRUD."""

    def __init__(self, session: Session, model: type[ModelType]):
        self.session = session
        self.model = model

    def create(self, entity: ModelType) -> ModelType:
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def get_by_id(self, entity_id: int) -> Optional[ModelType]:
        return self.session.get(self.model, entity_id)

    def get_all(self) -> List[ModelType]:
        return self.session.exec(select(self.model)).all()

    def update(self, entity: ModelType) -> ModelType:
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def delete(self, entity: ModelType) -> None:
        self.session.delete(entity)
        self.session.commit()
