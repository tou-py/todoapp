from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from models.models import User
from repositories.user_repo import UserRepository


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = await self.user_repo.get_user_by_email(email)
        if not user or not user.check_password(password) or not user.is_active:
            return None
        return user
