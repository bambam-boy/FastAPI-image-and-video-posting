import uuid
import os

from dotenv import load_dotenv
from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, models
from fastapi_users.authentication import (
    AuthenticationBackend, BearerTransport, JWTStrategy
)
from fastapi_users.db import SQLAlchemyUserDatabase
from app.database.db import get_user_db
from app.models.UserModels import User

load_dotenv()

KEY = os.getenv("JWT_SECRET_KEY")


class UserManger(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = KEY
    verification_token_secret = KEY


# TODO: use some of these fucntions
    # async def on_after_register(self, user: User, request: Optional[Request] = None):
    #     return await super().on_after_register(user, request)


async def get_user_manger(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManger(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_startegy():
    return JWTStrategy(secret=KEY, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_startegy
)

fastapi_user = FastAPIUsers[User, uuid.UUID](get_user_manger, [auth_backend])
current_active_user = fastapi_user.current_user(active=True)
