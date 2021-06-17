from fastapi import FastAPI

from .database import Base, engine
from .routers import edge, element, hello_world, node, resource

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

app.include_router(
    edge.router,
    prefix="/edge"
)
