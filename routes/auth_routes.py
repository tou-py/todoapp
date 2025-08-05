from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_session
from config.security import create_token
from config.settings import settings
from repositories.user_repo import UserRepository
from schemas.schemas import Token
from services.auth_service import authenticate_user

router = APIRouter(tags=["auth"])

@router.post('/login', response_model=Token)
async def login(email: str, password: str, session: AsyncSession = Depends(get_session)):
    user = await authenticate_user(session, email, password)
    if not user:
        raise HTTPException(status_code=404, detail="Incorrect email or password", headers={"WWW-Authenticate": "Bearer"})

    access_token = create_token(token_type='access', data={"sub": user.email})
    ref_token = create_token(token_type='refresh', data={"sub": user.email})

    return {
        "access_token": access_token,
        "refresh_token": ref_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
        ref_token: str,
        session: AsyncSession = Depends(get_session)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(ref_token, settings.SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_repo = UserRepository(session)
    user = await user_repo.get_user_by_email(email)
    if user is None or not user.is_active:
        raise credentials_exception

    access_token = create_token(token_type='access', data={"sub": user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
