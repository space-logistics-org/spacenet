"""
Endpoints to run trade studies of scenario variations.
"""

import os
from typing import List

from fastapi import APIRouter
from pydantic import Field

from spacenet.trades import TradeResult, TradeStudy, metric_names, run_trade

from .models import ScenarioRequest

router = APIRouter()

#: Number of cases above which cases are simulated in parallel processes.
PARALLEL_CASES = 6


class TradeRequest(ScenarioRequest):
    """Request to run a trade study of variations of a scenario."""

    study: TradeStudy = Field(..., description="Trade study")


@router.get("/metrics")
def get_metrics() -> List[str]:
    """Lists the metrics which a trade study can report."""
    return metric_names()


@router.post("/run")
def run(request: TradeRequest) -> TradeResult:
    """
    Simulates each case of a trade study and reports its metrics. Cases with
    invalid values report an error instead of metrics.
    """
    workers = None
    count = 1
    for variable in request.study.variables:
        count *= len(variable.values)
    if count >= PARALLEL_CASES:
        workers = min(4, os.cpu_count() or 1)
    return run_trade(request.scenario, request.study, workers=workers)
