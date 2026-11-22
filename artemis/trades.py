"""
Sensitivity of the reference Artemis campaign to its propellant logistics
parameters: each parameter of :class:`CampaignParameters` is varied in turn
over a range of published or notional values (one at a time), and the
campaign is regenerated (e.g., with a different number of tanker flights)
and simulated.

Usage: ``python artemis/trades.py`` prints a Markdown table.
"""

import sys
from dataclasses import replace
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

# pylint: disable=wrong-import-position
from artemis_add_campaign import CampaignParameters, build_scenario  # noqa: E402

from spacenet.simulation import FullSimulator, PropellantAnalysis  # noqa: E402
from spacenet.validation import number  # noqa: E402

#: Parameters and the values over which they vary (the first is the baseline).
PARAMETERS: List[Tuple[str, str, List[float]]] = [
    (
        "tanker_delivery",
        "Tanker propellant delivery (t)",
        [150_000.0, 100_000.0, 125_000.0],
    ),
    ("depot_boiloff_rate", "Depot boiloff (%/day)", [0.0005, 0.0002, 0.001, 0.002]),
    ("hls_boiloff_rate", "HLS boiloff (%/day)", [0.001, 0.0005, 0.0015]),
    ("transfer_loss", "Transfer loss (%)", [0.01, 0.0, 0.03]),
    ("tanker_interval_days", "Days between tanker flights", [6.0, 3.0, 12.0]),
    ("hls_dry_mass", "HLS dry mass (t)", [100_000.0, 85_000.0, 110_000.0]),
]

#: Display scale of each parameter.
SCALES = {
    "tanker_delivery": 1e-3,
    "depot_boiloff_rate": 100,
    "hls_boiloff_rate": 100,
    "transfer_loss": 100,
    "hls_dry_mass": 1e-3,
}


def evaluate(params: CampaignParameters) -> Dict[str, float]:
    """
    Simulates the campaign for a set of parameters.

    Returns:
        dict: tankers per landing, errors, the propellant (t) remaining in the
        Artemis III HLS when it is disposed of, and total boiloff (t).
    """
    tankers = params.tankers()
    simulator = FullSimulator(build_scenario(params))
    simulator.simulate()
    propellant = PropellantAnalysis.create(simulator)
    residual = sum(
        b.residual * b.unit_mass
        for b in propellant.budgets
        if b.vehicle_name == "Artemis III | HLS"
    )
    return {
        "tankers": tankers,
        "errors": len(simulator.spatial_errors),
        "hls_residual": residual / 1000,
        "boiloff": propellant.totals.boiloff_mass / 1000,
    }


def sensitivity() -> List[Tuple[str, float, Dict[str, float]]]:
    """
    Varies each parameter in turn from the baseline.

    Returns:
        [(parameter label, value, results)]: The cases (the baseline first).
    """
    baseline = CampaignParameters()
    cases = [("Baseline", float("nan"), evaluate(baseline))]
    for name, label, values in PARAMETERS:
        for value in values[1:]:
            params = replace(baseline, **{name: value})
            cases.append((label, value * SCALES.get(name, 1), evaluate(params)))
    return cases


def report(cases) -> str:
    """Formats the sensitivity cases as a Markdown table."""
    lines = [
        "| Parameter | Value | Tankers per landing | Errors | "
        "Artemis III HLS residual (t) | Campaign boiloff (t) |",
        "|---|---|---|---|---|---|",
    ]
    for label, value, result in cases:
        lines.append(
            f"| {label} | {'' if value != value else number(value)} "
            f"| {result['tankers']} | {result['errors']} "
            f"| {result['hls_residual']:.1f} | {result['boiloff']:.0f} |"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    print(report(sensitivity()))
