from app.models.ingrediente import Ingrediente
from app.core.uow import UnitOfWork

def create_ingrediente(data):
    with UnitOfWork() as uow:
        ingrediente = Ingrediente(**data.model_dump())
        return uow.ingredientes.create(ingrediente)

def get_all_ingredientes():
    with UnitOfWork() as uow:
        return uow.ingredientes.get_all()

def get_ingrediente(ingrediente_id: int):
    with UnitOfWork() as uow:
        return uow.ingredientes.get_by_id(ingrediente_id)

def update_ingrediente(ingrediente_id: int, data):
    with UnitOfWork() as uow:
        ingrediente = uow.ingredientes.get_by_id(ingrediente_id)
        if not ingrediente:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(ingrediente, key, value)

        return uow.ingredientes.update(ingrediente)

def delete_ingrediente(ingrediente_id: int):
    with UnitOfWork() as uow:
        ingrediente = uow.ingredientes.get_by_id(ingrediente_id)
        if not ingrediente:
            return None
        uow.ingredientes.delete(ingrediente)
        return True