from typing import Optional

from pydantic import EmailStr

from models.models import User
from repositories.user_repo import UserRepository
from schemas.schemas import UserUpdate, UserCreate
from services.base_service import BaseService


class UserService(BaseService[User, UserCreate, UserUpdate, UserRepository]):
    def __init__(self, user_repo: UserRepository):
        super().__init__(repository=user_repo, model=User)

    async def _validate_unique_email(self, email: EmailStr, exclude_user_id: Optional[str]) -> None:
        email_in_use = await self.repository.get_user_by_email(email)
        if email_in_use and str(email_in_use.id) != exclude_user_id:
            raise ValueError(f"Email {email} is already in use.")

    async def create(self, data: UserCreate) -> User:
        await self._validate_unique_email(data.email, exclude_user_id=None)

        user_model = self.model(**data.model_dump())
        user_model.set_password(user_model.password)

        return await self.repository.create(user_model)

    async def update(self, user_id: str, data: UserUpdate) -> Optional[User]:
        user_to_update = await self.get_by_id(user_id)
        if not user_to_update:
            raise ValueError(f"User with ID {user_id} not found.")

        # Manejo de actualización de contraseña
        if data.password:
            user_to_update.set_password(data.password)

        # Manejo de actualización de email
        if data.email and data.email != user_to_update.email:
            await self._validate_unique_email(data.email, exclude_user_id=user_id)
            user_to_update.email = data.email

        # Actualiza otros campos generales
        # exclude={'password', 'email'} para no intentar establecerlos de nuevo
        for key, value in data.model_dump(exclude={'password', 'email'}, exclude_unset=True).items():
            if hasattr(user_to_update, key):
                setattr(user_to_update, key, value)

        return await self.repository.update(user_to_update)

    async def patch(self, user_id: str, data: UserUpdate) -> Optional[User]:

        user_to_patch = await self.repository.get_object_by_id(user_id)
        if not user_to_patch:
            raise ValueError(f"User with ID {user_id} not found.")

        # validar email
        if data.email:
            if data.email != user_to_patch.email:
                await self._validate_unique_email(data.email, exclude_user_id=user_id)
            user_to_patch.email = data.email

        if data.password:
            user_to_patch.set_password(data.password)

        # actualizar otros campos
        for key, value in data.model_dump(exclude={'password', 'email'}, exclude_unset=True, exclude_none=True).items():
            if hasattr(user_to_patch, key):
                setattr(user_to_patch, key, value)

        return await self.repository.update(user_to_patch)
