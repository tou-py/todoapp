from typing import TypeVar, Type, Optional, List, Generic, cast

from sqlalchemy.exc import NoResultFound, SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel, select

Modeltype = TypeVar("Modeltype", bound=SQLModel)


class BaseRepository(Generic[Modeltype]):
    def __init__(self, session: AsyncSession, model: Type[Modeltype]):
        self.session = session
        self.model = model

    async def get_object_by_id(self, obj_id: str) -> Optional[Modeltype]:
        try:
            return await self.session.get(self.model, obj_id)
        except NoResultFound as ex:
            raise ex
        except SQLAlchemyError as ex:
            raise ex
        except Exception as ex:
            raise ex

    async def get_all(self, offset: int = 0, limit: int = 100) -> List[Modeltype]:
        try:
            statement = select(self.model).offset(offset).limit(limit)
            result = await self.session.execute(statement)
            # Retorna explícitamente una lista
            return cast(List[Modeltype], result.scalars().all())
        except SQLAlchemyError as ex:
            raise ex

    async def create(self, obj: Modeltype) -> Modeltype:
        try:
            self.session.add(obj)
            await self.session.commit()
            await self.session.refresh(obj)
            return obj
        except IntegrityError as ex:
            await self.session.rollback()
            raise ex
        except SQLAlchemyError as ex:
            await self.session.rollback()
            raise ex
        except Exception as ex:
            await self.session.rollback()
            raise ex

    # Aunque resulte repetitivo preferí separar create de update
    # a pesar de su similitud y de que SQLModel maneja upsert (actualiza si existe, crea si no)
    async def update(self, obj: Modeltype) -> Modeltype:
        try:
            self.session.add(obj)
            await self.session.commit()
            await self.session.refresh(obj)
            return obj
        except IntegrityError as ex:
            await self.session.rollback()
            raise ex
        except SQLAlchemyError as ex:
            await self.session.rollback()
            raise ex
        except Exception as ex:
            await self.session.rollback()
            raise ex

    async def delete(self, obj: Modeltype) -> bool:
        try:
            await self.session.delete(obj)
            await self.session.commit()
            return True
        except SQLAlchemyError as ex:
            await self.session.rollback()
            raise ex
        except Exception as ex:
            await self.session.rollback()
            raise ex
