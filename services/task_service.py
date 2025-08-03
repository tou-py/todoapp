from typing import Optional, List

from models.models import Task
from repositories.task_repo import TaskRepository
from repositories.user_repo import UserRepository
from schemas.schemas import TaskCreate, TaskUpdate
from services.base_service import BaseService


class TaskService(BaseService[Task, TaskCreate, TaskUpdate, TaskRepository]):
    def __init__(self, task_repo: TaskRepository, user_repo: UserRepository):
        super().__init__(repository=task_repo, model=Task)
        self.user_repo = user_repo

    def get_all_tasks(self, user_id: str, offset: int = 0, limit: int = 100) -> List[Task]:
        return self.repository.get_task_by_user(user_id=user_id, offset=offset, limit=limit)

    def create(self, obj_create_data: TaskCreate) -> Task:
        user = self.user_repo.get_object_by_id(str(obj_create_data.user_id))
        if not user:
            raise ValueError("User not found")

        if self.repository.get_task_by_title(obj_create_data.title, obj_create_data.user_id):
            raise ValueError("Task already exists")

        if obj_create_data.parent_id:
            parent_task = self.repository.get_object_by_id(str(obj_create_data.parent_id))
            if not parent_task:
                raise ValueError(f"Parent task with ID {obj_create_data.parent_id} not found.")
            if parent_task.level >= 3:
                raise ValueError("Parent task's level is too high (max 3) to add a subtask.")
            obj_create_data.level = parent_task.level + 1
        else:
            # Si no hay parent_id, el nivel siempre es 1
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

        if data.parent_id is not None:
            if data.parent_id:
                parent_task = self.repository.get_object_by_id(str(data.parent_id))
                if not parent_task:
                    raise ValueError(f"New parent task with ID {data.parent_id} not found.")
                if parent_task.level >= 3:
                    raise ValueError("New parent task's level is too high to add a subtask.")
                task.parent_id = data.parent_id
                task.level = parent_task.level + 1
            else:  # parent_id es None
                task.parent_id = None
                task.level = 1

        for key, value in data.model_dump(exclude={'title, parent_id'}, exclude_unset=True).items():
            if hasattr(task, key):
                setattr(task, key, value)

        return self.repository.update(task)

    def patch(self, task_id: str, data: TaskUpdate) -> Optional[Task]:
        task = self.repository.get_object_by_id(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found.")

        # Obtener los datos del esquema que realmente se enviaron (el parche)
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)

        if 'title' in update_data and update_data['title'] != task.title:
            existing_task = self.repository.get_task_by_title(update_data['title'], task.user_id)
            if existing_task and existing_task.id != task.id:
                raise ValueError(f"Task with title '{update_data['title']}' already exists for this user.")

        if 'parent_id' in update_data:
            new_parent_id = update_data['parent_id']
            if new_parent_id:
                parent_task = self.repository.get_object_by_id(str(new_parent_id))
                if not parent_task:
                    raise ValueError(f"New parent task with ID {new_parent_id} not found.")
                if parent_task.level >= 3:
                    raise ValueError("New parent task's level is too high (max 3) to add a subtask.")

                task.level = parent_task.level + 1
            else:  # parent_id es None
                task.level = 1
            task.parent_id = new_parent_id

        for key, value in update_data.items():
            if key not in ['title', 'parent_id'] and hasattr(task, key):
                setattr(task, key, value)

        return self.repository.update(task)
