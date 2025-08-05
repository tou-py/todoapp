from typing import List, Optional, cast

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from models.models import Task
from repositories.base_repo import BaseRepository


class TaskRepository(BaseRepository[Task]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Task)

    async def get_task_by_user(self, user_id: str, offset: int = 0, limit: int = 100) -> List[Task]:
        statement = select(Task).where(Task.user_id == user_id).offset(offset).limit(limit)
        result = await self.session.execute(statement)
        return cast(List[Task], result.scalars().first())

    async def get_task_by_title(self, title: str, user_id: str) -> Optional[Task]:
        statement = select(Task).where(Task.title == title, Task.user_id == user_id)
        result = await self.session.execute(statement)
        return result.scalars().first()
