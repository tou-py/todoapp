from typing import Optional

from pydantic import EmailStr
from sqlmodel import Session, select

from models.models import User
from repositories.base_repo import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: Session):
        super().__init__(session, User)

    def get_user_by_email(self, email: EmailStr) -> Optional[User]:
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()
