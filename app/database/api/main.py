from fastapi import FastAPI

from .routers import hello_world, element, resource, node
from .database import Base, engine

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
    prefix="/hello",
)

app.include_router(
    element.router,
    prefix="/element"
)

app.include_router(
    resource.router,
    prefix="/resource"
)

app.include_router(
    node.router,
    prefix="/node"
)

# TODO: need more routing stubs to exist to progress here?
