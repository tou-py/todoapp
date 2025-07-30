from typing import Optional, List

from sqlmodel import Session, select

from models.models import User, Task


class TaskService:
    def __init__(self, session: Session):
        self.session = session

    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        return self.session.get(Task, task_id)

    def get_task_by_user(self, user_id: str, offset: int = 0, limit: int = 100) -> List[Task]:
        statement = select(Task).where(Task.user_id == user_id).offset(offset).limit(limit)
        return List(self.session.exec(statement).all())

    def create(self, task_data: Task) -> Task:

        user = self.session.get(User, task_data)
        if not user:
            raise Exception("User not found")

        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)

        return task_data


    def update(self, task_id: str, task_data: Task) -> Optional[Task]:

        task = self.get_task_by_id(task_id)
        if not task:
            raise Exception("Task not found")

        for key, value in task_data.model_dump(exclude_unset=True).items():
            if hasattr(task, key):
                setattr(task, key, value)

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        return task

    def delete(self, task_id: str) -> bool:

        task = self.get_task_by_id(task_id)
        
        if not task:
            return False

        self.session.delete(task)
        self.session.commit()

        return True