from typing import Optional
from models.models import User
from repositories.user_repo import UserRepository
from schemas.schemas import UserUpdate, UserCreate
from services.base_service import BaseService


class UserService(BaseService[User, UserCreate, UserUpdate, UserRepository]):
    def __init__(self, user_repo: UserRepository):
        super().__init__(repository=user_repo, model=User)

    def create(self, data: UserCreate) -> User:
        existing_user = self.repository.get_user_by_email(data.email)
        if existing_user:
            raise ValueError(f'User {data.email} already exists')

        user_model = self.model(**data.model_dump())
        user_model.set_password(user_model.password)

        return self.repository.create(user_model)

    def update(self, user_id: str, data: UserUpdate) -> Optional[User]:
        user_to_update = self.repository.get_object_by_id(user_id)
        if not user_to_update:
            raise ValueError(f"User with ID {user_id} not found.")

        # Manejo de actualización de contraseña
        if data.password:
            user_to_update.set_password(data.password)

        # Manejo de actualización de email
        if data.email and data.email != user_to_update.email:
            existing_with_new_email = self.repository.get_user_by_email(data.email)
            if existing_with_new_email and str(existing_with_new_email.id) != user_id:  # Convertir a str para comparar
                raise ValueError(f'Email "{data.email}" already registered by another user.')
            user_to_update.email = data.email

        # Actualiza otros campos generales
        # exclude={'password', 'email'} para no intentar establecerlos de nuevo
        for key, value in data.model_dump(exclude={'password', 'email'}, exclude_unset=True).items():
            if hasattr(user_to_update, key):
                setattr(user_to_update, key, value)

        try:
            return self.repository.update(user_to_update)
        except Exception as e:
            raise ValueError(f"Error updating user: {e}") from e

