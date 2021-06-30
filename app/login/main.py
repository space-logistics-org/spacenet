import databases
import sqlalchemy
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi_users import FastAPIUsers, models
from fastapi_users.authentication import JWTAuthentication, CookieAuthentication
from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base

from typing import Optional
from pydantic import BaseModel

# define the application
app = FastAPI(
    title="SpaceNet Login",
    description="Application to login to SpaceNet.",
    version="0.0"
)


DATABASE_URL = "sqlite:///./userbase.db"
SECRET = "SECRET"

class User(models.BaseUser):
    pass


class UserCreate(models.BaseUserCreate):
    pass


class UserUpdate(User, models.BaseUserUpdate):
    pass


class UserDB(User, models.BaseUserDB):
    pass


database = databases.Database(DATABASE_URL)
Base: DeclarativeMeta = declarative_base()


class UserTable(Base, SQLAlchemyBaseUserTable):
    pass


engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
Base.metadata.create_all(engine)

users = UserTable.__table__
user_db = SQLAlchemyUserDatabase(UserDB, database, users)


def on_after_register(user: UserDB, request: Request):
    print(f"User {user.id} has registered.")


jwt_authentication = JWTAuthentication(
    secret=SECRET, lifetime_seconds=7200, tokenUrl="auth/jwt/login"
)
cookie_authentication = CookieAuthentication(
    secret=SECRET, lifetime_seconds=7200, cookie_secure=False
)

app = FastAPI()
fastapi_users = FastAPIUsers(
    user_db,
    [jwt_authentication, cookie_authentication],
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)
app.include_router(
    fastapi_users.get_auth_router(jwt_authentication), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_auth_router(cookie_authentication), prefix="/auth/cookie", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(on_after_register), prefix="/auth", tags=["auth"]
)
app.include_router(fastapi_users.get_users_router(), prefix="/users", tags=["users"])

@app.get("/secret")
async def secret(user: User = Depends(fastapi_users.current_user(active=True))):
    return {
        "secret": "secret"
    }

@app.get("/super-secret")
async def super_secret(user: User = Depends(fastapi_users.current_user(active=True,superuser=True))):
    return {
        "secret": "secret"
    }
app.mount("/", StaticFiles(directory="app/login/static", html=True), name="static")

@app.on_event("startup")
async def startup():
    await database.connect()
    try:
        await fastapi_users.create_user(
            UserCreate(
                email="admin@example.com",
                password="admin",
                is_superuser=True,
            )
        )
    except:
        print(f'Admin account already exists, skipping.')



@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
