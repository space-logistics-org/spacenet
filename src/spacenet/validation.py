"""
Validation of engineering models against published reference data.

A :class:`Reference` records a published value (or range) with its source.
A :class:`ValidationResult` compares a model value with a reference and
records how the reference relates to the model:

* ``validated``: the model value is computed independently of the reference
  (e.g., a launch vehicle capability simulated from stage masses), so the
  comparison tests the model;
* ``calibrated``: a model parameter was tuned to reproduce the reference, so
  the comparison only confirms the calibration;
* ``input``: the reference is used directly as a model input (e.g., a
  published delta-v), so the comparison confirms traceability.
"""

import math
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Iterable, List, Optional, Tuple, Union

from .schemas import Scenario
from .simulation import FullSimulator


class CheckKind(str, Enum):
    """Enumeration of the relations between a reference and the model."""

    VALIDATED = "validated"
    CALIBRATED = "calibrated"
    INPUT = "input"


class CheckStatus(str, Enum):
    """Enumeration of the outcomes of a comparison."""

    PASS = "pass"
    FAIL = "fail"


@dataclass(frozen=True)
class Reference:
    """
    A published value (or range) of a quantity with its source.
    """

    #: Unique key of the reference.
    key: str
    #: Description of the quantity.
    quantity: str
    #: Published value, or (minimum, maximum) range (None for an open bound).
    value: Union[float, Tuple[Optional[float], Optional[float]]]
    unit: str
    #: Citation of the source.
    source: str
    #: Location of the source (URL).
    url: str = ""
    #: Notes on the interpretation of the published value.
    note: str = ""

    @property
    def bounds(self) -> Tuple[float, float]:
        """The (minimum, maximum) of the published value."""
        if isinstance(self.value, tuple):
            low, high = self.value
            return (
                -math.inf if low is None else low,
                math.inf if high is None else high,
            )
        return (self.value, self.value)

    def describe(self) -> str:
        """Describes the published value."""
        low, high = self.bounds
        if low == high:
            return number(low)
        if math.isinf(low):
            return f"<= {number(high)}"
        if math.isinf(high):
            return f">= {number(low)}"
        return f"{number(low)} to {number(high)}"


def number(value: float) -> str:
    """Formats a value with four significant digits (and thousands separators)."""
    if value == 0 or not math.isfinite(value):
        return f"{value:g}"
    digits = max(0, 3 - int(math.floor(math.log10(abs(value)))))
    return f"{value:,.{digits}f}"


@dataclass(frozen=True)
class ValidationResult:
    """
    Comparison of a model value with a published reference.
    """

    reference: Reference
    kind: CheckKind
    #: Model value (in the unit of the reference).
    model: float
    #: Relative tolerance for a pass.
    tolerance: float
    status: CheckStatus
    #: Relative difference to the nearest bound of the reference (0 inside a range).
    difference: float
    #: Notes on how the model value is computed.
    note: str = ""


def compare(
    reference: Reference,
    model: float,
    kind: CheckKind = CheckKind.VALIDATED,
    tolerance: float = 0.0,
    note: str = "",
) -> ValidationResult:
    """
    Compares a model value with a reference: it passes if it lies within the
    published range widened by the relative tolerance.

    Args:
        reference (:obj:`Reference`): The reference.
        model (float): The model value.
        kind (:obj:`CheckKind`): The relation of the reference to the model.
        tolerance (float): The relative tolerance.
        note (str): Notes on how the model value is computed.

    Returns:
        :obj:`ValidationResult`: The comparison.
    """
    low, high = reference.bounds
    if model < low:
        difference = (model - low) / abs(low) if low else -math.inf
    elif model > high:
        difference = (model - high) / abs(high) if high else math.inf
    else:
        difference = 0.0
    passed = abs(difference) <= tolerance + 1e-12
    return ValidationResult(
        reference=reference,
        kind=CheckKind(kind),
        model=model,
        tolerance=tolerance,
        status=CheckStatus.PASS if passed else CheckStatus.FAIL,
        difference=difference,
        note=note,
    )


def is_feasible(scenario: Scenario) -> bool:
    """True, if a scenario simulates without spatial errors (e.g., delta-v)."""
    simulator = FullSimulator(scenario)
    simulator.simulate()
    return not simulator.spatial_errors


def max_payload(
    build: Callable[[float], Scenario],
    upper: float,
    lower: float = 0.0,
    precision: float = 10.0,
) -> float:
    """
    Finds the largest payload mass for which a scenario is feasible by
    bisection with the full simulator.

    Args:
        build (Callable[[float], Scenario]): Builds the scenario for a payload mass (kg).
        upper (float): A payload mass (kg) known to be infeasible.
        lower (float): A payload mass (kg) known to be feasible.
        precision (float): The precision (kg) of the result.

    Returns:
        float: The largest feasible payload mass (kg).
    """
    if not is_feasible(build(lower)):
        return math.nan
    while upper - lower > precision:
        middle = (lower + upper) / 2
        if is_feasible(build(middle)):
            lower = middle
        else:
            upper = middle
    return lower


def describe_difference(result: ValidationResult) -> str:
    """
    Describes the difference of a model value from its reference: the
    relative difference to the nearest bound, or "in range" for a value
    within a published range (or bound).
    """
    low, high = result.reference.bounds
    if result.difference == 0 and low != high:
        return "in range"
    if math.isinf(result.difference):
        return "outside"
    return f"{100 * result.difference:+.1f}%"


def describe_tolerance(result: ValidationResult) -> str:
    """Describes the relative tolerance of a comparison ("exact" if none)."""
    if result.tolerance <= 0:
        return "exact"
    return f"±{100 * result.tolerance:g}%"


def summarize(results: Iterable[ValidationResult]) -> str:
    """
    Summarizes validation results: the number of comparisons of each kind
    and the comparisons which fail.

    Args:
        results ([:obj:`ValidationResult`]): The results.

    Returns:
        str: The summary.
    """
    results = list(results)
    counts = [
        f"{sum(1 for r in results if r.kind == kind)} {kind.value}"
        for kind in CheckKind
        if any(r.kind == kind for r in results)
    ]
    failed = failures(results)
    outcome = (
        "all pass"
        if not failed
        else f"{len(failed)} fail ({', '.join(r.reference.quantity for r in failed)})"
    )
    return f"{len(results)} comparisons ({', '.join(counts)}): {outcome}."


def report_markdown(results: Iterable[ValidationResult]) -> str:
    """
    Formats validation results as a Markdown table preceded by a summary. A
    comparison passes if the model value lies within the published value (or
    range) widened by the relative tolerance.

    Args:
        results ([:obj:`ValidationResult`]): The results.

    Returns:
        str: The summary and table.
    """
    results = list(results)
    lines = [
        summarize(results),
        "",
        "| Quantity | Published | Model | Difference | Tolerance | Kind | Status "
        "| Source |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for result in results:
        ref = result.reference
        source = f"[{ref.source}]({ref.url})" if ref.url else ref.source
        lines.append(
            f"| {ref.quantity} ({ref.unit}) | {ref.describe()} | {number(result.model)} "
            f"| {describe_difference(result)} | {describe_tolerance(result)} "
            f"| {result.kind.value} | {result.status.value} | {source} |"
        )
    return "\n".join(lines)


def failures(results: Iterable[ValidationResult]) -> List[ValidationResult]:
    """Lists the results which fail."""
    return [r for r in results if r.status == CheckStatus.FAIL]
