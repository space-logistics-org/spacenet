"""
Tests of trade studies of scenario variations.
"""

import unittest

import pytest

from spacenet import schemas as s
from spacenet.trades import (
    MAX_CASES,
    TradeDesign,
    TradeStudy,
    Variable,
    cases,
    get_value,
    metric_names,
    run_trade,
    set_value,
)

from .simulation.util import ScenarioBuilder


def build():
    """A stage which burns 1000 m/s (feasible with 300 kg of fuel or more)."""
    b = ScenarioBuilder()
    stage = b.vehicle(name="Stage", mass=1000, fuel=1000, max_fuel=5000, isp=300)
    b.mission([b.create([stage], b.leo), b.burn_event([stage], days=1)])
    return b.build()


FUEL = "elementTemplates/name=Stage/propulsionSystems/0/fuelTank/contents/amount"


class TestPaths(unittest.TestCase):
    def setUp(self):
        self.data = {
            "items": [{"name": "A", "x": 1}, {"name": "B", "x": 2, "y": [5, 6]}]
        }

    def test_get_and_set(self):
        self.assertEqual(get_value(self.data, "items/name=B/x"), 2)
        self.assertEqual(get_value(self.data, "/items/1/y/0"), 5)
        set_value(self.data, "items/name=A/x", 10)
        set_value(self.data, "items/name=A/z", 3)  # an absent field is added
        set_value(self.data, "items/1/y/1", 7)
        self.assertEqual(self.data["items"][0], {"name": "A", "x": 10, "z": 3})
        self.assertEqual(self.data["items"][1]["y"], [5, 7])

    def test_invalid_paths(self):
        for path in ("items/name=C/x", "items/5/x", "missing/x", "items/0/x/y"):
            with self.subTest(path=path), self.assertRaises(KeyError):
                get_value(self.data, path)


class TestCases(unittest.TestCase):
    def study(self, design):
        return TradeStudy(
            variables=[
                Variable(name="a", path="items/name=A/x", values=[1, 2, 3]),
                Variable(name="b", path="items/name=B/x", values=[10, 20]),
            ],
            design=design,
        )

    def test_full_factorial(self):
        base = {"items": [{"name": "A", "x": 1}, {"name": "B", "x": 2}]}
        combinations = cases(self.study(TradeDesign.FULL_FACTORIAL), base)
        self.assertEqual(len(combinations), 6)
        self.assertIn({"a": 3, "b": 20}, combinations)

    def test_one_at_a_time(self):
        base = {"items": [{"name": "A", "x": 1}, {"name": "B", "x": 2}]}
        combinations = cases(self.study(TradeDesign.ONE_AT_A_TIME), base)
        # the baseline (1, 2), two other values of a, and two values of b
        self.assertEqual(
            combinations,
            [
                {"a": 1, "b": 2},
                {"a": 2, "b": 2},
                {"a": 3, "b": 2},
                {"a": 1, "b": 10},
                {"a": 1, "b": 20},
            ],
        )

    def test_too_many_cases(self):
        study = TradeStudy(
            variables=[
                Variable(name="a", path="x", values=list(range(MAX_CASES))),
                Variable(name="b", path="y", values=[1, 2]),
            ]
        )
        with self.assertRaises(ValueError):
            cases(study, {"x": 0, "y": 0})


class TestRunTrade(unittest.TestCase):
    def test_metrics_of_each_case(self):
        study = TradeStudy(
            variables=[Variable(name="fuel", path=FUEL, values=[100, 500, 1000])],
            metrics=["errorCount", "propellantBurnedMass"],
        )
        result = run_trade(build(), study)
        self.assertEqual(result.variables, ["fuel"])
        self.assertEqual(result.metrics, ["errorCount", "propellantBurnedMass"])
        errors = [c.metrics["errorCount"] for c in result.cases]
        # 100 kg of fuel cannot achieve the burn
        self.assertEqual(errors, [1, 0, 0])
        burned = [c.metrics["propellantBurnedMass"] for c in result.cases]
        self.assertEqual(burned[0], 100)
        # more fuel is a heavier stack which burns more fuel for the same delta-v
        self.assertGreater(burned[2], burned[1])

    def test_invalid_values_report_errors(self):
        study = TradeStudy(
            variables=[Variable(name="fuel", path=FUEL, values=["abc", 500])],
        )
        result = run_trade(build(), study)
        self.assertIsNotNone(result.cases[0].error)
        self.assertIsNone(result.cases[1].error)
        self.assertEqual(set(result.cases[1].metrics), set(metric_names()))

    def test_invalid_path_fails(self):
        study = TradeStudy(
            variables=[
                Variable(name="x", path="elementTemplates/name=None/mass", values=[1])
            ]
        )
        with self.assertRaises(KeyError):
            run_trade(build(), study)

    @pytest.mark.slow
    def test_parallel_cases_match(self):
        study = TradeStudy(
            variables=[Variable(name="fuel", path=FUEL, values=[100, 500, 1000])],
            metrics=["errorCount", "propellantBurnedMass"],
        )
        sequential = run_trade(build(), study)
        parallel = run_trade(build(), study, workers=2)
        self.assertEqual(
            [c.metrics for c in sequential.cases], [c.metrics for c in parallel.cases]
        )


class TestScenarioRoundTrip(unittest.TestCase):
    def test_unchanged_scenario_is_valid(self):
        scenario = build()
        data = scenario.model_dump(mode="json", by_alias=True, exclude_none=True)
        set_value(data, FUEL, 1000)
        self.assertEqual(s.Scenario.model_validate(data), scenario)
