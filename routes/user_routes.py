from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session
from starlette import status

from config.database import get_session
from repositories.user_repo import UserRepository
from schemas.schemas import UserResponse, UserCreate, UserUpdate
from services.user_service import UserService

def get_user_repository(session: Session = Depends(get_session)) -> UserRepository:
    return UserRepository(session)

def get_user_service(user_repo: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(user_repo)


router = APIRouter(prefix="/users", tags=["users"])


@router.post('/create', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create(user_data: UserCreate, user_service: UserService = Depends(get_user_service)):
    try:
        return user_service.create(user_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Database integrity error")
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get('/{user_id}', response_model=UserResponse, status_code=status.HTTP_200_OK)
def get(user_id: str, user_service: UserService = Depends(get_user_service)):
    user = user_service.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get('/limit={limit}/offset={offset}', status_code=status.HTTP_200_OK)
def get_all(limit: int = 100, offset: int = 0, user_service: UserService = Depends(get_user_service)):
    try:
        return user_service.get_all(limit, offset)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put('/{user_id}', response_model=UserResponse, status_code=status.HTTP_200_OK)
def update(user_id: str, user_update_data: UserUpdate, user_service: UserService = Depends(get_user_service)):
    try:
        updated_user = user_service.update(user_id, user_update_data)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.patch('/{user_id}', response_model=UserResponse, status_code=status.HTTP_200_OK)
def partial_update(user_id: str, user_to_patch: UserUpdate, user_service: UserService = Depends(get_user_service)):
    try:
        patched_user = user_service.patch(user_id, user_to_patch)
        if not patched_user:
            raise HTTPException(status_code=404, detail="User not found")
        return patched_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete('/{user_id}', status_code=status.HTTP_200_OK)
def delete(user_id: str, user_service: UserService = Depends(get_user_service)):
    try:
        if not user_service.delete(user_id):
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User deleted"}
    except Exception as ex:
        print(f"ERROR AQUI: {str(ex)}")
        raise HTTPException(status_code=500, detail="Internal server error")
