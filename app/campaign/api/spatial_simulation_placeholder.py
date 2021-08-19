from fastapi import APIRouter

from spacenet.schemas import Scenario

router = APIRouter()


@router.post("/", deprecated=True)
def simulate_scenario(scenario: Scenario):
    return scenario
