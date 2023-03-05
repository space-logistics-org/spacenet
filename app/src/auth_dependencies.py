"""
This module initializes authorization dependencies such as authentication tokens and the
user database.
"""
import os
import databases
import sqlalchemy
from fastapi import Request
from fastapi_users import FastAPIUsers, models
from fastapi_users.authentication import CookieAuthentication, JWTAuthentication
from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base

DATABASE_URL = "sqlite:///./userbase.db"
SECRET = os.getenv("SPACENET_AUTH_SECRET")
if SECRET is None:
    raise NameError("Authentication secret not defined. "
                    "Set the environment variable SPACENET_AUTH_SECRET to continue.")


class User(models.BaseUser):
    """
    Model for retrieving users.
    """
    pass


class UserCreate(models.BaseUserCreate):
    """
    Model for creating users.
    """
    pass


class UserUpdate(User, models.BaseUserUpdate):
    """
    Model for updating users.
    """
    pass


class UserDB(User, models.BaseUserDB):
    """
    Model representing a single row in the user database.
    """
    pass


database = databases.Database(DATABASE_URL)
Base: DeclarativeMeta = declarative_base()


class UserTable(Base, SQLAlchemyBaseUserTable):
    """
    Model representing the table of users in the user database.
    """
    pass


engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
Base.metadata.create_all(engine)

users = UserTable.__table__
user_db = SQLAlchemyUserDatabase(UserDB, database, users)


def on_after_register(user: UserDB, _request: Request):
    """
    Callback to use after a user registers.

    :param user: user who registered
    :param _request: request registering the user
    """
    print(f"User {user.id} has registered.")


jwt_authentication = JWTAuthentication(
    secret=SECRET, lifetime_seconds=7200, tokenUrl="auth/jwt/login"
)
cookie_authentication = CookieAuthentication(
    secret=SECRET, lifetime_seconds=7200, cookie_secure=False
)

fastapi_users = FastAPIUsers(
    user_db,
    [jwt_authentication, cookie_authentication],
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)

current_user = fastapi_users.current_user(active=True)
