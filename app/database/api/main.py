from fastapi import FastAPI

from .routers import hello_world
from .database import Base, SessionLocal, engine

# create the database if it does not yet exist
Base.metadata.create_all(bind=engine)

# define the application
app = FastAPI(
    title="SpaceNet Database API",
    description="API to perform SpaceNet database operations.",
    version="0.0"
)

# include any application routers
app.include_router(
    hello_world.router,
    prefix="/hello"
)
