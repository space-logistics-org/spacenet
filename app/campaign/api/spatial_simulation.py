from datetime import datetime
from typing import List, Union

from fastapi import APIRouter
from pydantic import BaseModel

from spacenet.schemas import Scenario
from spacenet.analysis.simulation import Simulation, SimResult, SimError

router = APIRouter()


class ResultAndErrors(BaseModel):
    result: SimResult
    errors: List[SimError]


@router.post("/", response_model=ResultAndErrors)
def simulate_scenario(scenario: Scenario) -> ResultAndErrors:
    sim = Simulation(scenario)
    sim.run()
    return ResultAndErrors(result=sim.result(), errors=sim.errors)


@router.post("/", response_model=ResultAndErrors)
def simulate_scenario_until(scenario: Scenario, stop_time: datetime) -> ResultAndErrors:
    sim = Simulation(scenario)
    sim.run(until=stop_time)
    return ResultAndErrors(result=sim.result(), errors=sim.errors)

