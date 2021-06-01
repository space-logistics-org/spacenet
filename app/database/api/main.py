from fastapi import FastAPI
from starlette.responses import RedirectResponse

# define the application
app = FastAPI(
    title="SpaceNet Database API",
    description="API to perform SpaceNet database operations.",
    version="0.0"
)

# include any application routers
from .routers import hello_world
app.include_router(
    hello_world.router,
    prefix="/hello_world"
)