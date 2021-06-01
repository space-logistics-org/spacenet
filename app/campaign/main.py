from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# define the application
app = FastAPI(
    title="SpaceNet Campaign Editor",
    description="Application to edit SpaceNet space exploration campaigns.",
    version="0.0"
)

# include any application routers
#app.include_router(...)

# mount the static directory
app.mount("/", StaticFiles(directory="app/campaign/static", html=True), name="static")
