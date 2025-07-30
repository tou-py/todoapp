from typing import Optional, List

from sqlmodel import Session, select

from models.models import User


class UserService:
    def __init__(self, session: Session):
        self.session = session

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        return self.session.get(User, user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first

    def get_all_users(self, offset: int = 0, limit: int = 100) -> List[User]:
        statement = select(User).offset(offset).limit(limit)
        return List(self.session.exec(statement).all())

    def create(self, user_data: User) -> User:

        existing_user = self.get_user_by_email(user_data.email)
        if existing_user:
            raise ValueError("User already exists")

        user_data.set_password(user_data.password)
        self.session.add(user_data)
        self.session.commit()
        self.session.refresh(user_data)
        return user_data

    def update(self, user_id: str, user_data: User) -> User:

        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User does not exist")

        for key, value in user_data.model_dump(exclude_unset=True).items():
            if key == "password" and value:
                user.set_password(value)
            elif hasattr(user, key):
                setattr(user, key, value)

    def delete(self, user_id: str) -> bool:
        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User does not exist")
        self.session.delete(user)
        self.session.commit()
        self.session.refresh(user)
        return True