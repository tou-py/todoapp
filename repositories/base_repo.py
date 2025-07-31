from typing import TypeVar, Type, Optional, List, Generic

from sqlmodel import Session, SQLModel, select

Modeltype = TypeVar("Modeltype", bound=SQLModel)

class BaseRepository(Generic[Modeltype]):
    def __init__(self, session: Session, model: Type[Modeltype]):
        self.session = session
        self.model = model

    def get_object_by_id(self, obj_id: str) -> Optional[Modeltype]:
        return self.session.get(self.model, obj_id)

    def get_all(self, offset: int = 0, limit: int = 100) -> List[Modeltype]:
        statement = select(self.model).offset(offset).limit(limit)
        return list(self.session.exec(statement).all())

    def create(self, obj: Modeltype) -> Modeltype:
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    # Aunque resulte repetitivo preferí separar create de update
    # a pesar de su similaridad y de que SQLModel maneja upsert (actualiza si existe, crea si no)
    def update(self, obj: Modeltype) -> Optional[Modeltype]:
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj


    def delete(self, obj_id: str) -> bool:
        self.session.delete(obj_id)
        self.session.commit()
        return True