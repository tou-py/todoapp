from typing import Optional, List

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlmodel import Session, select

from models.models import User, Task
from schemas.schemas import TaskCreate, TaskUpdate


class TaskService:
    def __init__(self, session: Session):
        self.session = session

    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        return self.session.get(Task, task_id)

    def get_task_by_user(self, user_id: str, offset: int = 0, limit: int = 100) -> List[Task]:
        statement = select(Task).where(Task.user_id == user_id).offset(offset).limit(limit)
        return list(self.session.exec(statement).all())

    def create(self, task_data: TaskCreate) -> Task:

        user = self.session.get(User, task_data.user_id)
        if not user:
            raise ValueError("User not found")

        existing_task_statement = select(Task).where(Task.title == task_data.title, Task.user_id == task_data.user_id)
        existing_task = self.session.exec(existing_task_statement).first()

        if existing_task:
            raise Exception(f"Task with title:{task_data.title} already exists for this user")

        new_task = Task.model_validate(task_data)

        self.session.add(new_task)

        try:
            self.session.commit()
            self.session.refresh(new_task)
            return new_task
        except IntegrityError as e:
            self.session.rollback()
            raise ValueError(f"An Integrity Error in the database has ocurred: {e}")
        except SQLAlchemyError as e:
            self.session.rollback()
            raise ValueError(f"A database error occurred: {e}")
        except Exception as e:
            self.session.rollback()
            raise ValueError(f"Failed to create new task: {e}")

    def update(self, task_id: str, task_data: TaskUpdate) -> Optional[Task]:

        task = self.get_task_by_id(task_id)
        if not task:
            return None

        update_data = task_data.model_validate(task_data)

        if "title" in update_data and update_data["title"] != task.title:
            existing_task_statement = select(Task).where(
                Task.title == update_data["title"],
                Task.user_id == task.user_id
            )
            existing_task = self.session.exec(existing_task_statement).first()
            if existing_task and existing_task.id != task_id:
                raise ValueError(f"Task with title:{update_data['title']} already exists for this user")

        for key, value in update_data.items():
            setattr(task, key, value)

        try:
            self.session.add(task)
            self.session.commit()
            self.session.refresh(task)
        except IntegrityError as e:
            self.session.rollback()
            raise ValueError(f"Failed to update task due to DB integrity error: {e.orig}")
        except SQLAlchemyError as e:
            self.session.rollback()
            raise ValueError(f"A database error occurred during update: {e}")
        except Exception as e:
            self.session.rollback()
            raise ValueError(f"An unexpected error occurred during update: {e}")

        return task

    def delete(self, task_id: str) -> bool:
        task = self.get_task_by_id(task_id)

        if not task:
            return False

        try:
            self.session.delete(task)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            raise ValueError(f"A database error occurred during deletion: {e}")
        except Exception as e:
            self.session.rollback()
            raise ValueError(f"An unexpected error occurred during deletion: {e}")
