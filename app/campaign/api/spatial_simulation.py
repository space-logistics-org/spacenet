from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from spacenet.schemas import Scenario
from spacenet.analysis.simulation import Simulation, SimResult, SimError

router = APIRouter()


class ResultAndErrors(BaseModel):
    result: SimResult
    errors: List[SimError]


@router.post("/", response_model=ResultAndErrors)
def simulate_scenario_until(
    scenario: Scenario, stop_time: Optional[datetime] = None
) -> ResultAndErrors:
    sim = Simulation(scenario)
    if stop_time is not None:
        sim.run(until=stop_time)
    else:
        sim.run()
    return ResultAndErrors(result=sim.result(), errors=sim.errors)
