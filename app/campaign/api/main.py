from fastapi import FastAPI

from . import demands

# define the application
app = FastAPI(
    title="SpaceNet Campaign API",
    description="API to perform SpaceNet campaign analysis.",
    version="0.0"
)

# include any application routers
app.include_router(
    demands.router,
    prefix="/demands",
)