from typing import TypeVar, Type, Optional, List, Generic

from sqlalchemy.exc import NoResultFound, SQLAlchemyError, IntegrityError
from sqlmodel import Session, SQLModel, select

Modeltype = TypeVar("Modeltype", bound=SQLModel)


class BaseRepository(Generic[Modeltype]):
    def __init__(self, session: Session, model: Type[Modeltype]):
        self.session = session
        self.model = model

    def get_object_by_id(self, obj_id: str) -> Optional[Modeltype]:
        try:
            return self.session.get(self.model, obj_id)
        except NoResultFound as ex:
            raise ex
        except SQLAlchemyError as ex:
            raise ex
        except Exception as ex:
            raise ex

    def get_all(self, offset: int = 0, limit: int = 100) -> List[Modeltype]:
        try:
            statement = select(self.model).offset(offset).limit(limit)
            return list(self.session.exec(statement).all())
        except SQLAlchemyError as ex:
            raise ex

    def create(self, obj: Modeltype) -> Modeltype:
        try:
            self.session.add(obj)
            self.session.commit()
            self.session.refresh(obj)
            return obj
        except IntegrityError as ex:
            self.session.rollback()
            raise ex
        except SQLAlchemyError as ex:
            self.session.rollback()
            raise ex
        except Exception as ex:
            self.session.rollback()
            raise ex

    # Aunque resulte repetitivo preferí separar create de update
    # a pesar de su similitud y de que SQLModel maneja upsert (actualiza si existe, crea si no)
    def update(self, obj: Modeltype) -> Modeltype:
        try:
            self.session.add(obj)
            self.session.commit()
            self.session.refresh(obj)
            return obj
        except IntegrityError as ex:
            self.session.rollback()
            raise ex
        except SQLAlchemyError as ex:
            self.session.rollback()
            raise ex
        except Exception as ex:
            self.session.rollback()
            raise ex

    def delete(self, obj: Modeltype) -> bool:
        try:
            self.session.delete(obj)
            self.session.commit()
            return True
        except SQLAlchemyError as ex:
            self.session.rollback()
            raise ex
        except Exception as ex:
            self.session.rollback()
            raise ex
