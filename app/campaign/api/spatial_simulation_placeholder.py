from datetime import datetime
from typing import List, Union, Dict, Set

from fastapi import APIRouter
from pydantic import BaseModel

from spacenet.schemas import Scenario
from spacenet.analysis.simulation import Simulation, SimError, SimNode, SimEdge

router = APIRouter()

@router.post("/")
def simulate_scenario(scenario: Scenario):
    return scenario
