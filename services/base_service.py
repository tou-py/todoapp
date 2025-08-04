from typing import TypeVar, Generic, Optional, List

from pydantic import BaseModel
from sqlmodel import SQLModel

# El modelo de DB a usar
ModelType = TypeVar('ModelType', bound=SQLModel)
# El esquema de Pydantic a crear
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
# El esquema de Pydantic a actualizar
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)
# El repositorio a usar
RepositoryType = TypeVar('RepositoryType')


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType, RepositoryType]):
    def __init__(self, repository: RepositoryType, model: type[ModelType]):
        self.repository = repository
        self.model = model

    async def get_by_id(self, object_id: str) -> Optional[ModelType]:
        return await self.repository.get_object_by_id(object_id)

    async def get_all(self, offset: int = 0, limit: int = 100) -> Optional[List[ModelType]]:
        return await self.repository.get_all(offset=offset, limit=limit)

    async def create(self, obj_create_data: CreateSchemaType) -> ModelType:
        obj_model = self.model(**obj_create_data.model_dump())
        return await self.repository.create(obj_model)

    async def update(self, object_id: str, obj_data: UpdateSchemaType) -> Optional[ModelType]:
        obj = await self.repository.get_object_by_id(object_id)
        if not obj:
            return None

        for key, value in obj_data.model_dump(exclude_unset=True).items():
            if hasattr(obj, key):
                setattr(obj, key, value)

        return await self.repository.update(obj)

    async def patch(self, object_id: str, obj_data: UpdateSchemaType) -> Optional[ModelType]:
        obj = await self.repository.get_object_by_id(object_id)
        if not obj:
            return None

        update_data = obj_data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)

        return await self.repository.update(obj, update_data)

    async def delete(self, object_id: str) -> bool:
        obj = await self.repository.get_object_by_id(object_id)
        if not obj:
            return False
        return await self.repository.delete(obj)
