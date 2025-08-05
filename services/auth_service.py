from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from models.models import User
from repositories.user_repo import UserRepository


async def authenticate_user(session: AsyncSession, email: str, password: str) -> Optional[User]:
    user_repo = UserRepository(session)
    user = await user_repo.get_user_by_email(email)
    if not user or not user.check_password(password) or not user.is_active:
        return None
    return user
