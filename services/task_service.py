from typing import Optional
from models.models import Task
from repositories.task_repo import TaskRepository
from repositories.user_repo import UserRepository
from schemas.schemas import TaskCreate, TaskUpdate
from services.base_service import BaseService


class TaskService(BaseService[Task, TaskCreate, TaskUpdate, TaskRepository]):
    def __init__(self, task_repo: TaskRepository, user_repo: UserRepository):
        super().__init__(repository=task_repo, model=Task)
        self.user_repo = user_repo

    def create(self, obj_create_data: TaskCreate) -> Task:
        user = self.user_repo.get_object_by_id(str(obj_create_data.user_id))
        if not user:
            raise ValueError("User not found")

        if self.repository.get_task_by_title(obj_create_data.title, obj_create_data.user_id):
            raise ValueError("Task already exists")

        if obj_create_data.parent_id:
            parent_task = self.repository.get_object_by_id(str(obj_create_data.parent_id))
            if not parent_task:
                raise ValueError("Parent not found")
            if parent_task.level >= 3:
                raise ValueError("Parent task's level top reached")
            obj_create_data.level = parent_task.level + 1
        else:
            obj_create_data.level = 1

        new_task = self.model(**obj_create_data.model_dump())

        return self.repository.create(new_task)

    def update(self, task_id: str, data: TaskUpdate) -> Optional[Task]:
        task = self.repository.get_object_by_id(task_id)
        if not task:
            raise ValueError("Task not found")

        if data.title and data.title != task.title:
            existing_task = self.repository.get_task_by_title(data.title, task.user_id)
            if existing_task and existing_task.id != task.id:
                raise ValueError("Task with same title already exists for this user")
            task.title = data.title

        for key, value in data.model_dump(exclude={'title'}, exclude_unset=True).items():
            if key == "parent_id" and value is not None:
                parent_task = self.repository.get_object_by_id(str(value))
                if not parent_task:
                    raise ValueError("New parent task not found.")
                if parent_task.level >= 4:
                    raise ValueError("New parent task's level is too high to add a subtask.")
                task.parent_id = value
                task.level = parent_task.level + 1
            elif key == "parent_id" and value is None:
                task.parent_id = None
                task.level = 1
            elif hasattr(task, key):
                setattr(task, key, value)

        return self.repository.update(task)


