from datetime import datetime
from typing import List, Union, Dict, Set

from fastapi import APIRouter
from pydantic import BaseModel

from spacenet.schemas import Scenario
from spacenet.analysis.simulation import Simulation, SimError, SimNode, SimEdge

router = APIRouter()


class SimResult(BaseModel):
    network: Dict[SimNode, Set[SimEdge]]
    end_time: datetime

    @staticmethod
    def from_sim(sim: Simulation) -> 'SimResult':
        return SimResult(
            network=sim.network,
            end_time=sim.current_time
        )


@router.get("/")
def simulate_scenario(scenario: Scenario) -> Union[SimResult, List[SimError]]:
    sim = Simulation(scenario)
    errors = sim.run()
    if errors:
        return errors
    return SimResult.from_sim(sim)