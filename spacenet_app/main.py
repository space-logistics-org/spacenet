"""
SpaceNet web application.

Launch with `uvicorn spacenet_app.main:app` from the project root.
"""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import spacenet

from .api import add_exception_handlers
from .api import router as api_router
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

#: Directory of the browser-based user interface.
STATIC_DIR = Path(__file__).resolve().parent / "static"


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Creates the user database and the administrator at startup."""
    await create_db_and_tables()
    await create_user(ADMIN_EMAIL, ADMIN_PASSWORD, True)
    yield


app = FastAPI(title="SpaceNet App", version=spacenet.__version__, lifespan=lifespan)

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
app.include_router(api_router, prefix="/api")
add_exception_handlers(app)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
async def get_user_interface():
    """Serves the browser-based user interface."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/public")
async def example_public_endpoint():
    return {"message": "Hello World"}


@app.get("/private")
async def example_private_endpoint(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}
