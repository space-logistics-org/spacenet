"""
Application programming interface of the SpaceNet web application.

All endpoints are stateless: requests carry the scenario to analyze.
"""

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse

from spacenet.simulation import ScenarioError

from . import analysis, exports, manifest, meta, propellant, scenario, trades

router = APIRouter()
router.include_router(meta.router, prefix="/meta", tags=["meta"])
router.include_router(scenario.router, tags=["scenario"])
router.include_router(analysis.router, tags=["analysis"])
router.include_router(propellant.router, prefix="/propellant", tags=["propellant"])
router.include_router(trades.router, prefix="/trades", tags=["trades"])
router.include_router(manifest.router, prefix="/manifest", tags=["manifest"])
router.include_router(exports.router, prefix="/export", tags=["export"])

#: Status code for a request which is well-formed but cannot be processed.
UNPROCESSABLE = 422


def add_exception_handlers(app: FastAPI):
    """
    Adds handlers which respond with status 422 (in the format of request
    validation errors) to scenarios which cannot be simulated.

    Args:
        app (:obj:`FastAPI`): The application.
    """

    @app.exception_handler(ScenarioError)
    async def handle_scenario_error(_: Request, error: ScenarioError):
        return JSONResponse(
            status_code=UNPROCESSABLE,
            content={
                "detail": [
                    {
                        "type": "scenario_error",
                        "msg": error.message,
                        "missionIndex": error.mission_index,
                        "eventIndex": error.event_index,
                    }
                ]
            },
        )

    @app.exception_handler(ValueError)
    async def handle_value_error(_: Request, error: ValueError):
        return JSONResponse(
            status_code=UNPROCESSABLE,
            content={"detail": [{"type": "value_error", "msg": str(error)}]},
        )
