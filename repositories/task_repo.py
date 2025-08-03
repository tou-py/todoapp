from typing import List, Optional

from sqlmodel import Session, select

from models.models import Task
from repositories.base_repo import BaseRepository


class TaskRepository(BaseRepository[Task]):
    def __init__(self, session: Session):
        super().__init__(session, Task)

    def get_task_by_user(self, user_id: str, offset: int = 0, limit: int = 100) -> List[Task]:
        statement = select(Task).where(Task.user_id == user_id).offset(offset).limit(limit)
        return list(self.session.exec(statement).all())

    def get_task_by_title(self, title: str, user_id: str) -> Optional[Task]:
        statement = select(Task).where(Task.title == title, Task.user_id == user_id)
        return self.session.exec(statement).first()
