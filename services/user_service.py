from typing import Optional, List

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlmodel import Session, select

from models.models import User
from schemas.schemas import UserUpdate, UserCreate


class UserService:
    def __init__(self, session: Session):
        self.session = session

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        return self.session.get(User, user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()

    def get_all_users(self, offset: int = 0, limit: int = 100) -> List[User]:
        statement = select(User).offset(offset).limit(limit)
        return list(self.session.exec(statement).all())

    def create(self, user_data: UserCreate) -> User:
        existing_user = self.get_user_by_email(user_data.email)
        if existing_user:
            raise ValueError("User already exists")

        user = User.model_validate(user_data)
        user.set_password(user.password)

        try:
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
            return user
        except IntegrityError as e:
            print(str(e))
            self.session.rollback()
            raise ValueError("Failed to create user due to DB integrity error")
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        except Exception as e:
            self.session.rollback()
            raise e

    def update(self, user_id: str, user_data: UserUpdate) -> Optional[User]:
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        update_data = user_data.model_dump(exclude_unset=True)

        if "password" in update_data:
            user.set_password(update_data["password"])
            del update_data["password"]

        # Validar email duplicado
        if "email" in update_data and update_data["email"] != user.email:
            existing = self.get_user_by_email(update_data["email"])
            if existing and existing.id != user_id:
                raise ValueError("Email already in use")

        for key, value in update_data.items():
            setattr(user, key, value)

        try:
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
        except IntegrityError as e:
            self.session.rollback()
            raise ValueError(f"Failed to update user due to DB integrity error: {e.orig}")
        except SQLAlchemyError as e:
            self.session.rollback()
            raise ValueError(f"A database error occurred during update: {e}")
        except Exception as e:
            self.session.rollback()
            raise ValueError(f"An unexpected error occurred during update: {e}")

        return user

    def delete(self, user_id: str) -> bool:
        user = self.get_user_by_id(user_id)
        if not user:
            return False

        try:
            self.session.delete(user)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            raise ValueError(f"A database error occurred during deletion: {e}")
        except Exception as e:
            self.session.rollback()
            raise ValueError(f"An unexpected error occurred during deletion: {e}")
