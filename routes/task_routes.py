from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Session
from starlette import status
from starlette.responses import Response

from config.database import get_session
from repositories.task_repo import TaskRepository
from repositories.user_repo import UserRepository
from routes.user_routes import get_user_repository
from schemas.schemas import TaskResponse, TaskCreate, TaskUpdate
from services.task_service import TaskService


async def get_task_repository(session: AsyncSession = Depends(get_session)):
    return TaskRepository(session)


async def get_task_service(task_repo: TaskRepository = Depends(get_task_repository),
                     user_repo: UserRepository = Depends(get_user_repository)) -> TaskService:
    return TaskService(task_repo, user_repo)


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post('/create', response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create(task_data: TaskCreate, task_service: TaskService = Depends(get_task_service)):
    try:
        return await task_service.create(task_data)
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/{task_id}', response_model=TaskResponse, status_code=status.HTTP_200_OK)
async def get(task_id: str, task_service: TaskService = Depends(get_task_service)):
    task = await task_service.get_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get('/limit={limit}/offset={offset}', status_code=status.HTTP_200_OK)
async def get_all(limit: int = 100, offset: int = 0, task_service: TaskService = Depends(get_task_service)):
    tasks = await task_service.get_all(limit=limit, offset=offset)
    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks found")
    return tasks


@router.get('/user={user_id}/limit={limit}/offset={offset}', status_code=status.HTTP_200_OK)
async def get_all_by_user(user_id: str, limit: int = 100, offset: int = 0,
                    task_service: TaskService = Depends(get_task_service)):
    tasks = await task_service.get_all_tasks(user_id=user_id, limit=limit, offset=offset)
    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks found")
    return tasks


@router.put('/{task_id}', response_model=TaskResponse, status_code=status.HTTP_200_OK)
async def update(task_id: str, task_data: TaskUpdate, task_service: TaskService = Depends(get_task_service)):
    try:
        updated_task = await task_service.update(task_id, task_data)
        if not updated_task:
            raise HTTPException(status_code=404, detail="Task not found")
        return updated_task
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch('/{task_id}', response_model=TaskResponse, status_code=status.HTTP_200_OK)
async def partial_update(task_id: str, task_to_patch: TaskUpdate, task_service: TaskService = Depends(get_task_service)):
    try:
        patched_task = await task_service.patch(task_id, task_to_patch)
        if not patched_task:
            raise HTTPException(status_code=404, detail="Task not found")
        return patched_task
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete('/{task_id}', status_code=status.HTTP_200_OK)
async def delete(task_id: str, task_service: TaskService = Depends(get_task_service)):
    try:
        if not await task_service.delete(task_id):
            raise HTTPException(status_code=404, detail="Task not found")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
