from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# define the application
app = FastAPI(
    title="SpaceNet",
    description="Modeling and simulation for space exploration campaign logistics.",
    version="3.0.0"
)


# mount constituent applications
from .database import main as database
app.mount('/database', database.app)

from .campaign import main as campaign
app.mount('/campaign', campaign.app)

# mount the static directory
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")