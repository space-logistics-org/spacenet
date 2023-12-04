import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from starlette.responses import RedirectResponse

import spacenet

from .utils.db import User, create_db_and_tables
from .utils.schemas import UserCreate, UserRead, UserUpdate
from .utils.users import (
    cookie_backend,
    create_user,
    current_active_user,
    current_superuser,
    fastapi_users,
    jwt_backend,
)
from .validation import router as validation_router

load_dotenv()
ADMIN_EMAIL = os.getenv("SPACENET_ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.getenv("SPACENET_ADMIN_PASSWORD", "admin")

app = FastAPI(title="SpaceNet App", version=spacenet.__version__)

app.include_router(
    fastapi_users.get_auth_router(cookie_backend), prefix="", tags=["auth"]
)
app.include_router(
    fastapi_users.get_auth_router(jwt_backend), prefix="/auth", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
    dependencies=[Depends(current_superuser)],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
app.include_router(validation_router, prefix="/validate", tags=["validation"])


@app.get("/")
async def temp_redirect_to_docs():
    return RedirectResponse(url="/docs")


@app.get("/public")
async def example_public_endpoint():
    return {"message": "Hello World"}


@app.get("/private")
async def example_private_endpoint(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}


@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()
    await create_user(ADMIN_EMAIL, ADMIN_PASSWORD, True)
