"""
Generates the fixtures of the parity tests by running the reference (Java)
implementation on the parity scenarios: the reference scenarios which it can
read and random scenarios restricted to the features it shares with the
Python implementation (see :class:`tests.simulation.generator.ScenarioGenerator`).

Usage (see :mod:`tests.parity.java` to locate the reference implementation)::

    python -m tests.parity.generate_fixtures [--seeds 30]

Each fixture is a folder in ``tests/parity/fixtures`` with the scenario (in a
JSON format which both implementations read) and the normalized outputs of
the reference implementation (see :mod:`tests.parity.normalize`). The file
``fixtures/reference.json`` records the commit of the reference
implementation which produced them.
"""

import argparse
import json
import shutil
import tempfile
from pathlib import Path

from tests.simulation.generator import random_scenario
from tests.simulation.util import load_scenario

from . import normalize
from .java import JavaReference
from .legacy import write_legacy

FIXTURES = Path(__file__).resolve().parent / "fixtures"

#: Reference scenarios which the reference implementation can read (the
#: others use features it lacks, e.g., reaction control systems).
REFERENCE_SCENARIOS = {
    "quick_start_2": "quick_start/completed_quick_start_2_w_db.json",
    "quick_start_3": "quick_start/completed_quick_start_3_wo_db.json",
    "artemis_2024": "artemis/artemis_campaign.json",
}

#: Seed of the first random parity scenario.
FIRST_SEED = 0


def parity_scenarios(seeds: int):
    """Lists the (name, scenario) of each parity scenario."""
    for name, path in REFERENCE_SCENARIOS.items():
        yield name, load_scenario(path)
    for seed in range(FIRST_SEED, FIRST_SEED + seeds):
        yield f"random_{seed:03d}", random_scenario(seed, java=True)


def java_outputs(java: JavaReference, scenario_path: Path, work: Path) -> dict:
    """Runs the reference implementation and normalizes its outputs."""
    outputs = {}
    for consume in (False, True):
        key = "consume" if consume else "default"
        results = {}
        for mode, normalizer in (
            ("demands-raw", normalize.raw_demands),
            ("demands-agg", normalize.aggregated_demands),
            ("auto-manifest", normalize.java_manifest),
        ):
            output = work / f"{mode}-{key}.json"
            java.run(mode, scenario_path, output, consume=consume)
            results[mode] = normalizer(json.loads(output.read_text(encoding="utf-8")))
        outputs[key] = results
    return outputs


def main(argv=None):
    """Regenerates the parity fixtures."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", maxsplit=1)[0])
    parser.add_argument(
        "--seeds", type=int, default=30, help="number of random scenarios"
    )
    args = parser.parse_args(argv)
    java = JavaReference()
    java.compile()
    if FIXTURES.exists():
        shutil.rmtree(FIXTURES)
    FIXTURES.mkdir(parents=True)
    with tempfile.TemporaryDirectory() as work:
        for name, scenario in parity_scenarios(args.seeds):
            folder = FIXTURES / name
            folder.mkdir()
            scenario_path = folder / "scenario.json"
            write_legacy(scenario, scenario_path)
            outputs = java_outputs(java, scenario_path, Path(work))
            with open(folder / "java.json", "w", encoding="utf-8", newline="\n") as f:
                json.dump(outputs, f, separators=(",", ":"))
                f.write("\n")
            print(f"{name}: {len(outputs['default']['demands-raw'])} raw demands")
    with open(FIXTURES / "reference.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(
            {
                "repository": "https://github.com/space-logistics-org/spacenet",
                "commit": java.commit,
                "seeds": args.seeds,
            },
            f,
            indent=2,
        )
        f.write("\n")


if __name__ == "__main__":
    main()
