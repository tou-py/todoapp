from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from models.models import PriorityEnum


class UserBase(BaseModel):
    first_names: str
    last_names: str
    email: EmailStr

    class ConfigDict:
        from_attributes = True

class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=64)


class UserUpdate(BaseModel):
    first_names: Optional[str] = None
    last_names: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime


class TaskBase(BaseModel):
    title: str = Field(min_length=5, max_length=100)
    description: Optional[str] = None
    completed: bool = False
    priority: PriorityEnum = PriorityEnum.PODER

    class ConfigDict:
        from_attributes = True


class TaskCreate(TaskBase):
    user_id: str


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = False
    priority: Optional[PriorityEnum] = None
    end_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None


class TaskResponse(TaskBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime