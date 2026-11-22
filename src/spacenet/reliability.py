"""
Monte Carlo reliability analysis: simulate a scenario with random part
failures and summarize the distribution of failures of each part and the
probability of exhausting its spares.

Each unit of a part with a mean time to failure (MTTF) fails at a constant
rate while it operates (for its duty cycle while its element is active), so
the number of failures over an interval is Poisson-distributed. A failure
demands a spare from the element, its carrier, or the elements at its
location; a demand which cannot be satisfied is a shortfall.
"""

import math
from concurrent.futures import ProcessPoolExecutor
from typing import Any, Dict, List, Optional

import numpy as np
from fastapi_camelcase import CamelModel
from pydantic import Field

from .schemas import Scenario
from .schemas.scenarios.scenario import PartFailureMode
from .simulation import FullSimulator

#: Maximum number of runs of a Monte Carlo study.
MAX_RUNS = 1000
#: Percentiles reported for the failures of each part.
PERCENTILES = (50, 90, 95, 99)


class MonteCarloStudy(CamelModel):
    """Number of runs and random seed of a Monte Carlo reliability study."""

    runs: int = Field(100, description="Number of runs", ge=1, le=MAX_RUNS)
    seed: int = Field(0, description="Seed of the first run (incremented)", ge=0)


class ReliabilityRun(CamelModel):
    """The failures and shortfalls of each part in one run."""

    index: int
    seed: int
    failures: Dict[str, float] = Field({}, description="Failures of each part")
    shortfalls: Dict[str, float] = Field(
        {}, description="Spares of each part demanded but not available"
    )
    error_count: int = Field(0, description="Number of simulation errors")
    error: Optional[str] = Field(None, description="Error if the run failed")


class PartReliability(CamelModel):
    """Distribution of the failures and shortfalls of a part over all runs."""

    part: str = Field(..., description="Part (resource) name")
    elements: List[str] = Field([], description="Elements which contain the part")
    operating_hours: float = Field(
        0.0, description="Operating time (unit-hours) of all units of the part"
    )
    expected: float = Field(0.0, description="Expected number of failures")
    mean: float = Field(0.0, description="Mean number of failures")
    std: float = Field(0.0, description="Standard deviation of the failures")
    percentiles: Dict[str, float] = Field(
        {}, description="Percentiles (50, 90, 95, 99) of the failures"
    )
    max: float = Field(0.0, description="Largest number of failures")
    histogram: List[int] = Field(
        [], description="Number of runs with 0, 1, 2, ... failures"
    )
    shortfall_probability: float = Field(
        0.0, description="Fraction of runs with a shortfall of spares"
    )
    mean_shortfall: float = Field(0.0, description="Mean shortfall (units)")


class ReliabilityResult(CamelModel):
    """The results of a Monte Carlo reliability study."""

    runs: int = 0
    seed: int = 0
    parts: List[PartReliability] = []
    shortfall_probability: float = Field(
        0.0, description="Fraction of runs with a shortfall of any part"
    )
    failed_runs: int = Field(0, description="Number of runs which failed")
    results: List[ReliabilityRun] = []


def run_once(
    scenario: Scenario, seed: int, index: int = 0
) -> tuple[ReliabilityRun, FullSimulator]:
    """
    Simulates a scenario with random part failures.

    Args:
        scenario (:obj:`Scenario`): The scenario.
        seed (int): The seed of the random number generator.
        index (int): The index of the run.

    Returns:
        (:obj:`ReliabilityRun`, :obj:`FullSimulator`): The run and simulator.
    """
    simulator = FullSimulator(scenario, part_failures=PartFailureMode.RANDOM, seed=seed)
    simulator.simulate()
    failures: Dict[str, float] = {}
    for record in simulator.failure_records:
        failures[record.part_name] = (
            failures.get(record.part_name, 0.0) + record.failures
        )
    shortfalls: Dict[str, float] = {}
    for demand_error in simulator.unsatisfied_demands:
        for demand in demand_error.demands:
            name = demand.resource.name
            if name in failures and demand.amount > 0:
                shortfalls[name] = shortfalls.get(name, 0.0) + demand.amount
    run = ReliabilityRun(
        index=index,
        seed=seed,
        failures=failures,
        shortfalls=shortfalls,
        error_count=len(simulator.spatial_errors),
    )
    return run, simulator


def _run(arguments) -> tuple[ReliabilityRun, Dict[str, Any]]:
    index, data, seed = arguments
    try:
        run, simulator = run_once(Scenario.model_validate(data), seed, index)
    except Exception as error:  # pylint: disable=broad-except
        return ReliabilityRun(index=index, seed=seed, error=str(error)), {}
    # the expected failures and operating time do not depend on the failures
    parts: Dict[str, Dict[str, Any]] = {}
    for record in simulator.failure_records:
        part = parts.setdefault(
            record.part_name, {"elements": [], "expected": 0.0, "hours": 0.0}
        )
        if record.element_name not in part["elements"]:
            part["elements"].append(record.element_name)
        part["expected"] += record.expected
        part["hours"] += record.operating_hours
    return run, parts


def summarize(
    runs: List[ReliabilityRun], parts: Dict[str, Dict[str, Any]], seed: int = 0
) -> ReliabilityResult:
    """
    Summarizes the runs of a Monte Carlo reliability study.

    Args:
        runs ([:obj:`ReliabilityRun`]): The runs.
        parts (dict): The elements, expected failures, and operating hours of
            each part.
        seed (int): The seed of the first run.

    Returns:
        :obj:`ReliabilityResult`: The result.
    """
    completed = [run for run in runs if run.error is None]
    count = len(completed)
    summaries = []
    for name in sorted(parts):
        info = parts[name]
        failures = np.array([run.failures.get(name, 0.0) for run in completed])
        shortfalls = np.array([run.shortfalls.get(name, 0.0) for run in completed])
        if count == 0:
            failures = shortfalls = np.zeros(1)
        histogram = np.bincount(np.rint(failures).astype(int)).tolist()
        summaries.append(
            PartReliability(
                part=name,
                elements=info["elements"],
                operating_hours=info["hours"],
                expected=info["expected"],
                mean=float(failures.mean()),
                std=float(failures.std(ddof=1)) if count > 1 else 0.0,
                percentiles={
                    str(p): float(np.percentile(failures, p)) for p in PERCENTILES
                },
                max=float(failures.max()),
                histogram=histogram,
                shortfall_probability=float(np.mean(shortfalls > 0)),
                mean_shortfall=float(shortfalls.mean()),
            )
        )
    return ReliabilityResult(
        runs=len(runs),
        seed=seed,
        parts=summaries,
        shortfall_probability=(
            sum(1 for run in completed if any(v > 0 for v in run.shortfalls.values()))
            / count
            if count
            else 0.0
        ),
        failed_runs=len(runs) - count,
        results=runs,
    )


def run_monte_carlo(
    scenario: Scenario, study: MonteCarloStudy, workers: Optional[int] = None
) -> ReliabilityResult:
    """
    Runs a Monte Carlo reliability study: simulates the scenario with random
    part failures (run ``i`` uses the seed ``study.seed + i``).

    Args:
        scenario (:obj:`Scenario`): The scenario.
        study (:obj:`MonteCarloStudy`): The study.
        workers (int): The number of worker processes (default: run sequentially).

    Returns:
        :obj:`ReliabilityResult`: The result.
    """
    data = scenario.model_dump(mode="json", by_alias=True, exclude_none=True)
    arguments = [(i, data, study.seed + i) for i in range(study.runs)]
    if workers and workers > 1 and len(arguments) > 1:
        chunksize = max(1, math.ceil(len(arguments) / (4 * workers)))
        with ProcessPoolExecutor(max_workers=min(workers, len(arguments))) as pool:
            outputs = list(pool.map(_run, arguments, chunksize=chunksize))
    else:
        outputs = [_run(a) for a in arguments]
    parts: Dict[str, Dict[str, Any]] = {}
    for _, info in outputs:
        if info:
            parts = info
            break
    return summarize([run for run, _ in outputs], parts, study.seed)


def poisson_shortfall_probability(expected: float, spares: int) -> float:
    """
    Gets the probability that a Poisson-distributed number of failures with
    a mean exceeds the number of spares.

    Args:
        expected (float): The expected number of failures.
        spares (int): The number of spares.

    Returns:
        float: The probability of more failures than spares.
    """
    term = cumulative = math.exp(-expected)
    for k in range(1, spares + 1):
        term *= expected / k
        cumulative += term
    return max(0.0, 1.0 - cumulative)
