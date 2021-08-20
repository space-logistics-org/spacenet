"""
This module includes application routers and static files used for the database editor.
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

# define the application
app = FastAPI(
    title="SpaceNet Database Editor",
    description="Application to edit SpaceNet database objects.",
    version="0.0"
)

# mount constituent applications
from .api import main as api
app.mount('/api', api.app)

# mount the static directory
app.mount("/", StaticFiles(directory="app/database/static", html=True), name="static")
