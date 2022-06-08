"""
This module includes application routers and static files used for campaign analysis.
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# define the application
app = FastAPI(
    title="SpaceNet Campaign Editor",
    description="Application to edit SpaceNet space exploration campaigns.",
    version="0.0"
)

# include any application routers
from .api import main as api
app.mount("/api", api.app)

# mount the static directory
app.mount("/", StaticFiles(directory="app/src/campaign/static", html=True), name="static")
