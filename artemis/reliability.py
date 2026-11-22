"""
Monte Carlo reliability of the ISRU pilot plant of the reference Artemis
campaign: the campaign is simulated with random failures of the (notional)
electrolyzer stack and excavator drive actuators of the plant, which demand
spares from the kit delivered with it.

The simulated probability of exhausting the spares of each part is compared
with the Poisson distribution of failures (a verification of the Monte Carlo
model), and the spares required for 95% confidence are reported.

Usage: ``python artemis/reliability.py [runs]`` prints a Markdown table.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# pylint: disable=wrong-import-position
from artemis_add_campaign import CampaignParameters, build_scenario  # noqa: E402

from spacenet.reliability import (  # noqa: E402
    MonteCarloStudy,
    ReliabilityResult,
    poisson_shortfall_probability,
    run_monte_carlo,
)
from spacenet.validation import number  # noqa: E402


def spares_for(expected: float, confidence: float = 0.95) -> int:
    """Gets the fewest spares with at most 1 - confidence risk of a shortfall."""
    spares = 0
    while poisson_shortfall_probability(expected, spares) > 1 - confidence:
        spares += 1
    return spares


def report(result: ReliabilityResult, params: CampaignParameters) -> str:
    """Formats the result of the reliability study as a Markdown table."""
    spares = dict(
        zip(("Electrolyzer Stack", "Excavator Drive Actuator"), params.isru_spares)
    )
    lines = [
        "| Part | Operating time (unit-h) | Expected failures | Mean (simulated) "
        "| 95th percentile | Spares | P(shortfall) simulated | P(shortfall) Poisson "
        "| Spares for 95% |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for part in result.parts:
        count = spares.get(part.part, 0)
        lines.append(
            f"| {part.part} | {number(part.operating_hours)} "
            f"| {part.expected:.2f} | {part.mean:.2f} "
            f"| {part.percentiles['95']:.0f} | {count} "
            f"| {100 * part.shortfall_probability:.1f}% "
            f"| {100 * poisson_shortfall_probability(part.expected, count):.1f}% "
            f"| {spares_for(part.expected)} |"
        )
    lines.append(
        f"\nProbability of a shortfall of any spare: "
        f"{100 * result.shortfall_probability:.1f}% ({result.runs} runs, "
        f"seed {result.seed})."
    )
    return "\n".join(lines)


if __name__ == "__main__":
    RUNS = int(sys.argv[1]) if len(sys.argv) > 1 else 500
    PARAMS = CampaignParameters()
    RESULT = run_monte_carlo(
        build_scenario(PARAMS),
        MonteCarloStudy(runs=RUNS, seed=0),
        workers=min(4, os.cpu_count() or 1),
    )
    print(report(RESULT, PARAMS))
