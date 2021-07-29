from fastapi import FastAPI

from . import demands, spatial_simulation, spatial_simulation_placeholder

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

app.include_router(
    spatial_simulation.router,
    prefix="/simulation"
)

app.include_router(
    spatial_simulation_placeholder.router,
    prefix="/simulation_placeholder"
)