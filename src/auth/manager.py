from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin, exceptions, models, schemas

from auth.utils import get_user_db
from auth.utils import User



# Ключе Secret обычно переносят его в секреты(.env)
SECRET = "SECRET"


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    """Класс, который управляет созданием пользователей."""
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        """Регистрация пользователя."""
        #TO DO пользователь зарегистрировался.
        print(f"User {user.id} has registered.")

    async def create(
        self,
        user_create: schemas.UC,
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> models.UP:
        """Create a user in database."""
        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user is not None:
            raise exceptions.UserAlreadyExists()

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)
        # Cust. По умолчанию,когда пользователь регистрируется у него будет role_id=1(user)
        user_dict["role_id"] = 1

        created_user = await self.user_db.create(user_dict)

        await self.on_after_register(created_user, request)

        return created_user

    #TO DO  async def on_after_forgot_password & async def on_after_request_verify

async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)