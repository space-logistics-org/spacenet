import os.path

from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi_users.user import UserAlreadyExists
from pydantic import EmailStr

from .database import main as database_app
from .campaign import main as campaign

from .auth_dependencies import (
    User,
    UserCreate,
    cookie_authentication,
    database,
    fastapi_users,
    jwt_authentication,
)

# define the application
app = FastAPI(
    title="SpaceNet",
    description="Modeling and simulation for space exploration campaign logistics.",
    version="3.0.0",
)

# mount constituent applications


app.mount("/database", database_app.app)

app.mount("/campaign", campaign.app)

app.include_router(
    fastapi_users.get_auth_router(jwt_authentication), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_auth_router(cookie_authentication),
    prefix="/auth/cookie",
    tags=["auth"],
)

app.include_router(fastapi_users.get_users_router(), prefix="/users", tags=["users"])


@app.get("/secret")
async def secret(_user: User = Depends(fastapi_users.current_user(active=True))):
    return {"secret": "secret"}


@app.get("/super-secret")
async def super_secret(
        _user: User = Depends(fastapi_users.current_user(active=True, superuser=True))
):
    return {"secret": "secret"}


# mount the static directory
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")


@app.on_event("startup")
async def startup():
    await database.connect()
    try:
        await fastapi_users.create_user(
            UserCreate.parse_file(os.path.join(os.path.dirname(__file__), "admin_user.json"))
        )
    except UserAlreadyExists:
        print(f"Admin account already exists, skipping.")
    except FileNotFoundError:
        raise NameError("Administrator credentials not defined. "
                        "Run \"python -m app.provide_secrets\" from root directory "
                        "to configure admin credentials.")


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
