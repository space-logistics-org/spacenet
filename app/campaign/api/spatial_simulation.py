from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from spacenet.schemas import Scenario
from spacenet.analysis.simulation import Simulation, SimResult, SimError

router = APIRouter()


class ResultAndErrors(BaseModel):
    result: SimResult
    errors: List[SimError]


@router.post("/", response_model=ResultAndErrors)
def simulate_scenario(
    scenario: Scenario, days_to_run_for: Optional[float] = None
) -> ResultAndErrors:
    try:
        sim = Simulation(scenario)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=str(ve))  # TODO: format this better
    if days_to_run_for is None:
        sim.run()
    else:
        try:
            stop_date = scenario.startDate + timedelta(days=days_to_run_for)
        except OverflowError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="provided \"days_to_run_for\" causes overflow")
        sim.run(until=stop_date)
    return ResultAndErrors(result=sim.result(), errors=sim.errors)
