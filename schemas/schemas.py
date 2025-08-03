from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field

from models.models import PriorityEnum


class UserBase(BaseModel):
    first_names: str = Field(None, min_length=3, max_length=64)
    last_names: str = Field(None, min_length=3, max_length=64)
    email: EmailStr = Field(None, min_length=3, max_length=64)

    # Le dice a pydantic que mapee desde los atributos del ORM
    class ConfigDict:
        from_attributes = True


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=64)


class UserUpdate(BaseModel):
    first_names: Optional[str] = Field(None, min_length=3, max_length=64)
    last_names: Optional[str] = Field(None, min_length=3, max_length=64)
    email: Optional[EmailStr] = Field(None, min_length=3, max_length=64)
    password: Optional[str] = Field(None, min_length=3, max_length=64)

    class ConfigDict:
        from_attributes = True


class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime


class TaskBase(BaseModel):
    title: str = Field(min_length=5, max_length=100)
    description: Optional[str] = Field(None, max_length=512)
    completed: bool = False
    priority: PriorityEnum = PriorityEnum.PODER
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    level: Optional[int] = 1

    class ConfigDict:
        from_attributes = True


class TaskCreate(TaskBase):
    level: int = Field(default=1)
    user_id: str
    parent_id: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[PriorityEnum] = None
    started_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    parent_id: Optional[str] = None
    level: Optional[int] = None

    class ConfigDict:
        from_attributes = True


# Una representación mínima del usuario
class UserResponseForTask(BaseModel):
    id: str
    first_names: str
    last_names: str
    email: EmailStr

    class ConfigDict:
        from_attributes = True


# Para una representación mínima de las tareas
class MinimalTaskResponse(BaseModel):
    id: str
    title: str
    completed: bool
    priority: PriorityEnum

    class ConfigDict:
        from_attributes = True


# Respuesta principal al hacer get de una tarea
class TaskResponse(TaskBase):
    id: str
    created_at: datetime
    updated_at: datetime
    user: UserResponseForTask
    parent_id: Optional[str] = None
    subtasks: List[MinimalTaskResponse] = []
