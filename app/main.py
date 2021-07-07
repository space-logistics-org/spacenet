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
from .dependencies import fastapi_users, jwt_authentication, cookie_authentication, on_after_register, User, UserCreate, database

# define the application
app = FastAPI(
    title="SpaceNet",
    description="Modeling and simulation for space exploration campaign logistics.",
    version="3.0.0"
)

# mount constituent applications
from .database import main as database_app
app.mount('/database', database_app.app)

from .campaign import main as campaign
app.mount('/campaign', campaign.app)


app.include_router(
    fastapi_users.get_auth_router(jwt_authentication), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_auth_router(cookie_authentication), prefix="/auth/cookie", tags=["auth"]
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

# mount the static directory
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")

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