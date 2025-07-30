import secrets
from datetime import datetime
from enum import Enum
from typing import Optional

from passlib.context import CryptContext
from sqlmodel import Field, SQLModel, Relationship

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PriorityEnum(str, Enum):
    URGENCIA = "URGENCIA"
    NECESIDAD = "NECESIDAD"
    DEBER = "DEBER"
    PODER = "PODER"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(default_factory=lambda: secrets.token_urlsafe(8)[:8], primary_key=True)
    first_names: str = Field(nullable=False, min_length=3, max_length=64)
    last_names: str = Field(nullable=False, min_length=3, max_length=64)
    email: str = Field(
        nullable=False,
        unique=True,
        index=True,
        max_length=64,
    )
    password: str = Field(nullable=False, min_length=8)

    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now()
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(),
        sa_column_kwargs={"onupdate": lambda: datetime.now()},
    )

    # Este campo establece la relacion mediante el ORM entre el usuario y sus tareas
    tasks: list["Task"] = Relationship(back_populates="user")

    def set_password(self, password: str) -> None:
        self.password = pwd_context.hash(password)

    def check_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password)

    def __repr__(self):
        return f'<User(email={self.email}, first_name={self.first_names}, last_name={self.last_names})>'


class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: str = Field(default_factory=lambda: secrets.token_urlsafe(8)[:8], primary_key=True)
    title: str = Field(min_length=5, max_length=100)
    description: Optional[str] = Field(max_length=256)
    completed: bool = Field(default=False)
    priority: PriorityEnum = Field(default=PriorityEnum.PODER)
    started_at: Optional[datetime] = Field(default_factory=lambda: datetime.now())
    end_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    # aquí de la misma manera, esto garantiza la relacion desde el ORK
    user: "User" = Relationship(back_populates="tasks")
    # Este es el campo que va a figurar como fk
    user_id: str = Field(foreign_key="users.id", nullable=False)

    # La intención es que una tarea puede estar formada por varias otras menores
    # La clave foránea apunta a la ID de la tarea padre.
    parent_id: Optional[str] = Field(foreign_key="tasks.id", default=None)

    parent: Optional["Task"] = Relationship(
        back_populates="subtasks",
        sa_relationship_kwargs={"remote_side": "Task.id"}  # Indica que el lado remoto es la ID de la propia Task
    )
    subtasks: list["Task"] = Relationship(
        back_populates="parent"
    )

    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now()
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(),
        sa_column_kwargs={"onupdate": lambda: datetime.now()},
    )

    def __repr__(self):
        return f'<Task(title={self.title}, completed={self.completed}, priority={self.priority})>'
