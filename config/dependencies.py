from typing import AsyncGenerator

from fastapi import HTTPException, status
from fastapi.params import Depends, Path
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from config.security import oauth2_scheme, ALGORITHM, SECRET_KEY
from models.models import User
from repositories.task_repo import TaskRepository
from repositories.user_repo import UserRepository
from services.auth_service import AuthService
from services.task_service import TaskService
from services.user_service import UserService

from .database import async_session

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def get_user_repository(session: AsyncSession = Depends(get_session)) -> UserRepository:
    return UserRepository(session)


async def get_task_repository(session: AsyncSession = Depends(get_session)):
    return TaskRepository(session)


async def get_user_service(user_repo: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(user_repo)


async def get_task_service(task_repo: TaskRepository = Depends(get_task_repository),
                     user_repo: UserRepository = Depends(get_user_repository)) -> TaskService:
    return TaskService(task_repo, user_repo)


async def get_auth_service(session: AsyncSession = Depends(get_session)) -> AuthService:
    return AuthService(session)


async def get_current_user(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get('sub')
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_repo = UserRepository(session)
    user = await user_repo.get_user_by_email(email)
    if user is None or not user.is_active:
        raise credentials_exception
    return user


async def is_owner_or_admin_user(
    current_user: User = Depends(get_current_user),
    user_id: str = Path(...)
):
    if current_user.is_admin:
        return current_user

    if str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the owner of this user account."
        )

    return current_user

def admin_required(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action"
        )
    return current_user

async def is_owner_or_admin_task(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    task_id: str = Path(...)
):
    if current_user.is_admin:
        return current_user

    task_repo = TaskRepository(session)
    task = await task_repo.get_object_by_id(task_id)

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    if task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the owner of this task."
        )

    return current_user