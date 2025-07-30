from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session
from starlette import status

from config.database import get_session
from models.models import User
from schemas.schemas import UserResponse, UserCreate, UserUpdate
from services.user_service import UserService


def get_user_service(session: Session = Depends(get_session)) -> UserService:
    return UserService(session)

router = APIRouter(prefix="/users", tags=["users"])

@router.post('/create', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create(user_data: UserCreate, user_service: UserService = Depends(get_user_service)):
    user_model = User(**user_data.model_dump())
    try:
        user = user_service.create(user_model)
        return user
    except (IntegrityError, ValidationError, ValueError, Exception) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get('/{id}', response_model=UserResponse, status_code=status.HTTP_200_OK)
def get(user_id: str, user_service: UserService = Depends(get_user_service)):
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.put('/{id}', response_model=UserResponse, status_code=status.HTTP_200_OK)
def update(user_id: str, user_update_data: UserUpdate, user_service: UserService = Depends(get_user_service)):
    updated_user = user_service.update(user_id, user_update_data)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated_user

@router.delete('/{id}', status_code=status.HTTP_200_OK)
def delete(user_id: str, user_service: UserService = Depends(get_user_service)):
    if not user_service.delete(user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"message": "User deleted"}