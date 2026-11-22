"""
Endpoints to run Monte Carlo reliability studies of part failures.
"""

import os

from fastapi import APIRouter
from pydantic import Field

from spacenet.reliability import MonteCarloStudy, ReliabilityResult, run_monte_carlo

from .models import ScenarioRequest

router = APIRouter()

#: Number of runs above which runs are simulated in parallel processes.
PARALLEL_RUNS = 6


class MonteCarloRequest(ScenarioRequest):
    """Request to run a Monte Carlo reliability study of a scenario."""

    study: MonteCarloStudy = Field(
        MonteCarloStudy(), description="Monte Carlo reliability study"
    )


@router.post("/run")
def run(request: MonteCarloRequest) -> ReliabilityResult:
    """
    Simulates a scenario repeatedly with random failures of the parts which
    define a mean time to failure, and reports the distribution of failures
    of each part and the probability of exhausting its spares.
    """
    workers = None
    if request.study.runs >= PARALLEL_RUNS:
        workers = min(4, os.cpu_count() or 1)
    result = run_monte_carlo(request.scenario, request.study, workers=workers)
    if result.failed_runs == result.runs:
        raise ValueError(result.results[0].error)
    return result
