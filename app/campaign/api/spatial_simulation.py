from typing import List, Union

from fastapi import APIRouter

from spacenet.schemas import Scenario
from spacenet.analysis.simulation import Simulation, SimResult, SimError

router = APIRouter()


@router.post("/", response_model=Union[SimResult, List[SimError]])
def simulate_scenario(scenario: Scenario) -> Union[SimResult, List[SimError]]:
    sim = Simulation(scenario)
    sim.run()
    return sim.result()
