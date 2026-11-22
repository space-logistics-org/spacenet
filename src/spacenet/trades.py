"""
Trade studies: simulate variations of a scenario and compare their measures
of effectiveness.

A :class:`Variable` sets a field of the scenario (addressed by a path in the
JSON representation of the scenario) to each of its values. A
:class:`TradeStudy` combines variables in a full-factorial or one-at-a-time
design and lists the metrics to report for each case.

Paths separate keys, list indices, and list selectors with ``/``; a selector
``key=value`` selects the first list item whose key equals the value, e.g.,
``elementTemplates/name=HLS/propulsionSystems/0/fuelTank/boiloffRate`` or
``network/edges/name=LLO-LSP/burns/1/deltaV``.
"""

import itertools
import math
from concurrent.futures import ProcessPoolExecutor
from enum import Enum
from typing import Any, Dict, List, Optional

from fastapi_camelcase import CamelModel
from pydantic import Field

from .schemas import Scenario
from .simulation import FullSimulator
from .simulation.analysis.simulation import MeasureTotals

#: Maximum number of cases of a trade study.
MAX_CASES = 500


class TradeDesign(str, Enum):
    """Enumeration of the designs of a trade study."""

    #: Every combination of the values of all variables.
    FULL_FACTORIAL = "Full Factorial"
    #: Each value of each variable with the other variables at their base values.
    ONE_AT_A_TIME = "One at a Time"


class Variable(CamelModel):
    """A field of the scenario which takes each of a list of values."""

    name: str = Field(..., description="Variable name")
    path: str = Field(
        ..., description="Path of the field in the JSON representation of the scenario"
    )
    values: List[Any] = Field(..., description="Values of the field", min_length=1)


class TradeStudy(CamelModel):
    """Variables, design, and metrics of a trade study."""

    variables: List[Variable] = Field(..., min_length=1)
    design: TradeDesign = Field(TradeDesign.FULL_FACTORIAL)
    metrics: List[str] = Field(
        [], description="Metrics to report (default: all metrics)"
    )


class TradeCase(CamelModel):
    """The values and metrics of one case of a trade study."""

    index: int
    values: Dict[str, Any] = Field({}, description="Value of each variable")
    metrics: Dict[str, float] = Field({}, description="Value of each metric")
    error: Optional[str] = Field(None, description="Error if the case failed")


class TradeResult(CamelModel):
    """The cases of a trade study."""

    variables: List[str] = []
    metrics: List[str] = []
    cases: List[TradeCase] = []


#: Metrics reported in addition to the total measures of effectiveness.
COUNT_METRICS = (
    "errorCount",
    "warningCount",
    "unsatisfiedDemandCount",
    "unsatisfiedDemandMass",
)


def metric_names() -> List[str]:
    """Lists the names of the available metrics."""
    return list(COUNT_METRICS) + [
        field.alias or name for name, field in MeasureTotals.model_fields.items()
    ]


# ------------------------------------------------------------------ paths


class PathError(KeyError, ValueError):
    """An invalid path of a field of a JSON representation."""

    def __str__(self):
        return str(self.args[0]) if self.args else ""


def _segments(path: str) -> List[str]:
    return [segment for segment in path.strip("/").split("/") if segment]


def _child(node: Any, segment: str, path: str) -> Any:
    if isinstance(node, list):
        if "=" in segment:
            key, value = segment.split("=", 1)
            for item in node:
                if isinstance(item, dict) and str(item.get(key)) == value:
                    return item
            raise PathError(f"{path}: no item with {key}={value}")
        try:
            return node[int(segment)]
        except (ValueError, IndexError) as error:
            raise PathError(f"{path}: invalid index {segment}") from error
    if isinstance(node, dict):
        if segment not in node:
            raise PathError(f"{path}: no field {segment}")
        return node[segment]
    raise PathError(f"{path}: cannot select {segment} of a value")


def get_value(data: Any, path: str) -> Any:
    """
    Gets the value of a field of a JSON representation.

    Args:
        data: The JSON representation (dictionaries and lists).
        path (str): The path of the field.

    Returns:
        The value.
    """
    node = data
    for segment in _segments(path):
        node = _child(node, segment, path)
    return node


def set_value(data: Any, path: str, value: Any):
    """
    Sets the value of a field of a JSON representation (an absent field of an
    object is added).

    Args:
        data: The JSON representation (dictionaries and lists).
        path (str): The path of the field.
        value: The value.
    """
    segments = _segments(path)
    if not segments:
        raise PathError("Empty path")
    node = data
    for segment in segments[:-1]:
        node = _child(node, segment, path)
    last = segments[-1]
    if isinstance(node, dict):
        node[last] = value
    elif isinstance(node, list):
        node[int(last)] = value
    else:
        raise PathError(f"{path}: cannot set {last} of a value")


# ------------------------------------------------------------------ cases


def cases(study: TradeStudy, base: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Lists the variable values of each case of a trade study.

    Args:
        study (:obj:`TradeStudy`): The trade study.
        base (dict): The JSON representation of the base scenario.

    Returns:
        [dict]: The value of each variable in each case.
    """
    names = [v.name for v in study.variables]
    if study.design == TradeDesign.FULL_FACTORIAL:
        combinations = [
            dict(zip(names, values))
            for values in itertools.product(*(v.values for v in study.variables))
        ]
    else:
        baseline = {v.name: get_value(base, v.path) for v in study.variables}
        combinations = [dict(baseline)]
        for variable in study.variables:
            for value in variable.values:
                case = dict(baseline, **{variable.name: value})
                if case not in combinations:
                    combinations.append(case)
    if len(combinations) > MAX_CASES:
        raise ValueError(
            f"The trade study has {len(combinations)} cases (at most {MAX_CASES})."
        )
    return combinations


def evaluate(scenario: Scenario) -> Dict[str, float]:
    """
    Simulates a scenario and gets its metrics.

    Args:
        scenario (:obj:`Scenario`): The scenario.

    Returns:
        dict: The value of each metric.
    """
    simulator = FullSimulator(scenario)
    simulator.simulate()
    totals = MeasureTotals.create(simulator).model_dump(by_alias=True)
    metrics = {
        "errorCount": float(len(simulator.spatial_errors)),
        "warningCount": float(len(simulator.warnings)),
        "unsatisfiedDemandCount": float(len(simulator.unsatisfied_demands)),
        "unsatisfiedDemandMass": sum(
            d.demands.total_mass for d in simulator.unsatisfied_demands
        ),
    }
    metrics.update({k: float(v) for k, v in totals.items()})
    return metrics


def _run_case(arguments) -> TradeCase:
    index, base, variables, values, metrics = arguments
    try:
        data = _copy(base)
        for variable in variables:
            set_value(data, variable["path"], values[variable["name"]])
        scenario = Scenario.model_validate(data)
        result = evaluate(scenario)
        if metrics:
            result = {name: result.get(name, math.nan) for name in metrics}
        return TradeCase(index=index, values=values, metrics=result)
    except Exception as error:  # pylint: disable=broad-except
        return TradeCase(index=index, values=values, error=str(error))


def _copy(data):
    if isinstance(data, dict):
        return {k: _copy(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_copy(v) for v in data]
    return data


def run_trade(
    scenario: Scenario, study: TradeStudy, workers: Optional[int] = None
) -> TradeResult:
    """
    Runs a trade study: simulates each case and gets its metrics.

    Args:
        scenario (:obj:`Scenario`): The base scenario.
        study (:obj:`TradeStudy`): The trade study.
        workers (int): The number of worker processes (default: run sequentially).

    Returns:
        :obj:`TradeResult`: The result.
    """
    base = scenario.model_dump(mode="json", by_alias=True, exclude_none=True)
    for variable in study.variables:
        get_value(base, variable.path.rsplit("/", 1)[0] or "/")  # check the path
    combinations = cases(study, base)
    variables = [v.model_dump() for v in study.variables]
    arguments = [
        (index, base, variables, values, list(study.metrics))
        for index, values in enumerate(combinations)
    ]
    if workers and workers > 1 and len(arguments) > 1:
        with ProcessPoolExecutor(max_workers=min(workers, len(arguments))) as pool:
            results = list(pool.map(_run_case, arguments))
    else:
        results = [_run_case(a) for a in arguments]
    return TradeResult(
        variables=[v.name for v in study.variables],
        metrics=list(study.metrics) or metric_names(),
        cases=results,
    )
