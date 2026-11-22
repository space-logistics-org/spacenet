"""
Tests of the parity of the Python implementation with the reference (Java)
implementation, using fixtures of the outputs of its headless modes (see
:mod:`tests.parity.generate_fixtures`) so that the tests do not require Java.

The demand analyses (raw and aggregated demands, with and without consuming
existing resources) must match. The automatic manifests must pack the same
amount of each resource for each supply point; their containers and the
mass loaded on each transport must match except for the known differences
listed in :data:`KNOWN_DIFFERENCES`, each of which is explained (and checked
to still differ, so that the list stays up to date).
"""

import json
import logging
import math
import unittest
from pathlib import Path

from spacenet.schemas import Scenario
from spacenet.simulation import (
    AggregatedDemandsAnalysis,
    DemandSimulator,
    RawDemandsAnalysis,
    SimManifest,
)

from . import normalize

FIXTURES = Path(__file__).resolve().parent / "fixtures"

#: Reasons for known differences between the automatic manifests.
OVER_CAPACITY_FLIGHT = (
    "the reference implementation loads containers on flights which exceed "
    "their cargo mass capacity (and then fail during simulation)"
)
EARTH_DEMANDS = (
    "the reference implementation manifests demands on the surface of Earth, "
    "carrying them on a round trip from Earth"
)
PARTIAL_PACKING = (
    "the reference implementation only packs a demand in a container which "
    "fits all of it; here any amount which fits can be packed, so containers "
    "are filled (and then loaded) differently"
)

#: Known differences of the automatic manifests by fixture, settings
#: ("default" or "consume"), and aspect ("containers" or "transports").
KNOWN_DIFFERENCES = {
    ("quick_start_2", "default", "containers"): PARTIAL_PACKING,
    ("quick_start_2", "default", "transports"): PARTIAL_PACKING,
    ("quick_start_2", "consume", "containers"): PARTIAL_PACKING,
    ("quick_start_2", "consume", "transports"): PARTIAL_PACKING,
    ("random_005", "default", "containers"): PARTIAL_PACKING,
    ("random_005", "consume", "containers"): PARTIAL_PACKING,
    ("random_008", "default", "transports"): OVER_CAPACITY_FLIGHT,
    ("random_008", "consume", "transports"): OVER_CAPACITY_FLIGHT,
    # (random_015 also loads containers on a flight over capacity)
    ("random_015", "default", "transports"): EARTH_DEMANDS,
    ("random_015", "consume", "transports"): EARTH_DEMANDS,
    ("random_016", "default", "containers"): PARTIAL_PACKING,
    ("random_016", "default", "transports"): PARTIAL_PACKING,
    ("random_016", "consume", "containers"): PARTIAL_PACKING,
    ("random_016", "consume", "transports"): PARTIAL_PACKING,
    ("random_019", "default", "transports"): OVER_CAPACITY_FLIGHT,
    ("random_020", "default", "transports"): OVER_CAPACITY_FLIGHT,
    ("random_020", "consume", "transports"): OVER_CAPACITY_FLIGHT,
    ("random_022", "default", "transports"): OVER_CAPACITY_FLIGHT,
    ("random_027", "default", "containers"): PARTIAL_PACKING,
    ("random_027", "default", "transports"): PARTIAL_PACKING,
    ("random_027", "consume", "containers"): PARTIAL_PACKING,
    ("random_027", "consume", "transports"): PARTIAL_PACKING,
}


def fixtures():
    """Lists the fixture folders."""
    return sorted(p for p in FIXTURES.iterdir() if (p / "java.json").exists())


def close(expected, actual) -> bool:
    """Compares normalized results with a tolerance for numbers."""
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        return math.isclose(expected, actual, rel_tol=1e-9, abs_tol=1e-5)
    if isinstance(expected, list) and isinstance(actual, list):
        return len(expected) == len(actual) and all(
            close(e, a) for e, a in zip(expected, actual)
        )
    if isinstance(expected, dict) and isinstance(actual, dict):
        return expected.keys() == actual.keys() and all(
            close(expected[k], actual[k]) for k in expected
        )
    return expected == actual


def python_outputs(scenario: Scenario, consume: bool) -> dict:
    """Gets the normalized outputs of the Python implementation."""
    simulator = DemandSimulator(scenario, demands_satisfied=consume)
    simulator.simulate()
    manifest_simulator = DemandSimulator(
        scenario, demands_satisfied=consume, packing_demands_added=False
    )
    manifest_simulator.simulate()
    manifest = SimManifest(manifest_simulator)
    manifest.auto_manifest()
    return {
        "demands-raw": normalize.raw_demands(
            RawDemandsAnalysis.create(simulator).model_dump(mode="json", by_alias=True)
        ),
        "demands-agg": normalize.aggregated_demands(
            AggregatedDemandsAnalysis.create(simulator).model_dump(
                mode="json", by_alias=True
            )
        ),
        "auto-manifest": normalize.python_manifest(manifest),
    }


class TestJavaParity(unittest.TestCase):
    """Compares each fixture with the Python implementation."""

    @classmethod
    def setUpClass(cls):
        logging.disable(logging.WARNING)
        cls.results = {}
        for folder in fixtures():
            scenario = Scenario.model_validate_json(
                (folder / "scenario.json").read_text(encoding="utf-8")
            )
            java = json.loads((folder / "java.json").read_text(encoding="utf-8"))
            for key, consume in (("default", False), ("consume", True)):
                cls.results[(folder.name, key)] = (
                    java[key],
                    python_outputs(scenario, consume),
                )

    @classmethod
    def tearDownClass(cls):
        logging.disable(logging.NOTSET)

    def test_fixtures_exist(self):
        names = [f.name for f in fixtures()]
        self.assertIn("quick_start_2", names)
        self.assertGreaterEqual(len([n for n in names if n.startswith("random_")]), 30)
        reference = json.loads((FIXTURES / "reference.json").read_text())
        self.assertEqual(len(reference["commit"]), 40)

    def test_raw_demands(self):
        for (name, key), (java, python) in self.results.items():
            with self.subTest(name, settings=key):
                self.assertTrue(
                    close(java["demands-raw"], python["demands-raw"]),
                    f"java {java['demands-raw']}\npython {python['demands-raw']}",
                )

    def test_aggregated_demands(self):
        for (name, key), (java, python) in self.results.items():
            for part in ("nodes", "edges"):
                with self.subTest(name, settings=key, part=part):
                    expected = java["demands-agg"][part]
                    actual = python["demands-agg"][part]
                    self.assertTrue(
                        close(expected, actual), f"java {expected}\npython {actual}"
                    )

    def test_packed_amounts(self):
        for (name, key), (java, python) in self.results.items():
            with self.subTest(name, settings=key):
                expected = java["auto-manifest"]["packed"]
                actual = python["auto-manifest"]["packed"]
                self.assertTrue(
                    close(expected, actual), f"java {expected}\npython {actual}"
                )

    def test_containers_and_transports(self):
        found = {}
        for (name, key), (java, python) in self.results.items():
            for aspect in ("containers", "transports"):
                same = close(
                    java["auto-manifest"][aspect], python["auto-manifest"][aspect]
                )
                if not same:
                    found[(name, key, aspect)] = True
                known = (name, key, aspect) in KNOWN_DIFFERENCES
                with self.subTest(name, settings=key, aspect=aspect):
                    if known:
                        self.assertFalse(same, "a known difference no longer differs")
                    else:
                        self.assertTrue(same, "an unknown difference")
        self.assertEqual(
            sorted(k for k in KNOWN_DIFFERENCES if k not in found),
            [],
            "known differences which no longer differ",
        )


if __name__ == "__main__":
    unittest.main()
