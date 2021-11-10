"""
This module defines routes for analysis of campaigns via spatial simulation.
"""
from datetime import timedelta
from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from spacenet.analysis.checked_scenario import CheckedScenario
from spacenet.analysis.exceptions import SimException
from spacenet.analysis.simulation import Simulation, SimResult, SimError

router = APIRouter()


class ResultAndErrors(BaseModel):
    """
    A representation of both the result of a simulation and the errors that resulted.
    """
    result: SimResult
    errors: List[SimError]


@router.post("/", response_model=ResultAndErrors)
def simulate_scenario(
    scenario: CheckedScenario,
    time_to_run_for: Optional[timedelta] = None,
    propulsive: bool = False,
) -> ResultAndErrors:
    """
    Perform a spatial simulation analysis on the provided scenario, providing the resulting
    network and any errors which occurred running the simulation.
    """
    try:
        sim = Simulation(scenario, propulsive=propulsive)
    except SimException as se:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(se)
        )  # TODO: format this better
    if time_to_run_for is None:
        sim.run()
    else:
        try:
            stop_date = scenario.startDate + time_to_run_for
        except OverflowError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='provided "days_to_run_for" causes overflow',
            )
        sim.run(until=stop_date)
    return ResultAndErrors(result=sim.result, errors=sim.errors)
