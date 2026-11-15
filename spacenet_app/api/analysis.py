"""
Endpoints to analyze and simulate scenarios.
"""

from fastapi import APIRouter

from spacenet.simulation import (
    DemandsAnalysis,
    EventEvaluation,
    MissionsAnalysis,
    SimulationAnalysis,
    StateAnalysis,
)

from .models import DemandsRequest, EvaluateRequest, ScenarioRequest, StateRequest

router = APIRouter()

SECONDS_PER_DAY = 24 * 60 * 60


@router.post("/missions/analyze")
def analyze_missions(request: ScenarioRequest) -> MissionsAnalysis:
    """
    Simulates the events of a scenario to find the errors and warnings of
    each mission and event and the location of each element over time.
    """
    return MissionsAnalysis.create(request.scenario)


@router.post("/events/state")
def get_state(request: StateRequest) -> StateAnalysis:
    """
    Simulates a scenario up to (but not including) events of a mission at a
    time and priority and returns the elements at each location.
    """
    return StateAnalysis.create(
        request.scenario,
        request.mission_index,
        request.mission_time.total_seconds() / SECONDS_PER_DAY,
        request.priority,
        request.exclude_event_index,
    )


@router.post("/events/evaluate")
def evaluate_event(request: EvaluateRequest) -> EventEvaluation:
    """
    Executes a (draft) event of a mission in the simulation state before it
    and returns its errors, burns, transport duration and capacity, and a
    suggestion for the time and location of a following event.
    """
    return EventEvaluation.create(
        request.scenario, request.mission_index, request.event, request.event_index
    )


@router.post("/demands/analyze")
def analyze_demands(request: DemandsRequest) -> DemandsAnalysis:
    """
    Simulates the demands of a scenario and aggregates them to the
    transports from which they could be supplied.
    """
    return DemandsAnalysis.create(
        DemandsAnalysis.simulate(
            request.scenario,
            estimate_container_masses=request.options.estimate_container_masses,
            consume_existing_resources=request.options.consume_existing_resources,
        )
    )


@router.post("/simulate")
def simulate(request: ScenarioRequest) -> SimulationAnalysis:
    """
    Executes a full simulation of a scenario (including its manifest) and
    returns the errors, measures of effectiveness, and network history.
    """
    return SimulationAnalysis.create(request.scenario)
