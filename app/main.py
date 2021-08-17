import os.path

from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi_users.user import UserAlreadyExists
from pydantic import EmailStr, ValidationError

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
        ADMIN_EMAIL = os.getenv("SPACENET_ADMIN_EMAIL")
        ADMIN_EMAIL = "admin@example.org"
        if ADMIN_EMAIL is None:
            raise NameError("Administrator email not defined. "
                            "Set the environment variable SPACENET_ADMIN_EMAIL to continue.")
        ADMIN_PASSWORD = os.getenv("SPACENET_ADMIN_PASSWORD")
        ADMIN_PASSWORD = "password"
        if ADMIN_PASSWORD is None:
            raise NameError("Administrator password not defined. "
                            "Set the environment variable SPACENET_ADMIN_PASSWORD to continue.")
        try:
            await fastapi_users.create_user(
                UserCreate(
                    email=EmailStr(ADMIN_EMAIL),
                    password=ADMIN_PASSWORD,
                    is_superuser=True
                )
            )
        except ValidationError:
            raise ValueError(f"{ADMIN_EMAIL} is not a valid email")
    except UserAlreadyExists:
        print(f"Admin account already exists, skipping.")


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
