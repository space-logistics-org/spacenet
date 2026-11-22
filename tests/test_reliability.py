"""
Tests of part failures and Monte Carlo reliability analysis.
"""

import unittest
from datetime import timedelta

from spacenet import schemas as s
from spacenet.reliability import (
    MonteCarloStudy,
    poisson_shortfall_probability,
    run_monte_carlo,
    run_once,
)
from spacenet.simulation import FullSimulator

from .simulation.util import ScenarioBuilder


def build(spares=1, days=20, mttf_hours=240.0, state="Active", earth=False):
    """
    A pump (the spare resource) of a plant fails every 10 days on average
    while the plant is active; a kit holds spare pumps.
    """
    b = ScenarioBuilder()
    plant = b.element(
        "Plant",
        mass=100,
        parts=[
            s.Part(
                resource=b.spare.id,
                mean_time_to_failure=timedelta(hours=mttf_hours),
                quantity=1,
            )
        ],
        states=[s.State(name="Operating", type=state)],
        current_state_index=0,
    )
    kit = b.container(
        "Spares Kit",
        max_cargo_mass=100,
        contents=[s.ResourceAmount(resource=b.spare.id, amount=spares)],
    )
    site = b.ksc if earth else b.lsp
    b.mission(
        [
            b.create([plant, kit], site),
            b.create([b.element("Marker")], site, days=days),
        ]
    )
    return b.build()


class TestPartFailures(unittest.TestCase):
    def simulate(self, scenario, mode=None, seed=None):
        simulator = FullSimulator(scenario, part_failures=mode, seed=seed)
        simulator.simulate()
        return simulator

    def test_not_modeled_by_default(self):
        sim = self.simulate(build())
        self.assertEqual(sim.failure_records, [])
        self.assertEqual(sim.unsatisfied_demands, [])

    def test_expected_failures(self):
        sim = self.simulate(build(spares=1), s.PartFailureMode.EXPECTED)
        (record,) = sim.failure_records
        self.assertAlmostEqual(record.operating_hours, 480)
        self.assertAlmostEqual(record.expected, 2)
        self.assertAlmostEqual(record.failures, 2)
        # one failure is replaced from the kit and one is a shortfall
        (shortfall,) = sim.unsatisfied_demands
        self.assertEqual([d.amount for d in shortfall.demands], [1])

    def test_configuration_enables_failures(self):
        scenario = build()
        scenario.configuration.part_failures = s.PartFailureMode.EXPECTED
        self.assertEqual(len(self.simulate(scenario).failure_records), 1)

    def test_inactive_elements_do_not_fail(self):
        sim = self.simulate(build(state="Dormant"), s.PartFailureMode.EXPECTED)
        self.assertEqual(sim.failure_records, [])

    def test_elements_on_earth_do_not_fail(self):
        sim = self.simulate(build(earth=True), s.PartFailureMode.EXPECTED)
        self.assertEqual(sim.failure_records, [])

    def test_random_failures_are_reproducible(self):
        scenario = build(days=200)
        first, _ = run_once(scenario, seed=7)
        second, _ = run_once(scenario, seed=7)
        self.assertEqual(first.failures, second.failures)
        self.assertEqual(float(first.failures["Spare"]).is_integer(), True)
        counts = {run_once(scenario, seed=i)[0].failures["Spare"] for i in range(10)}
        self.assertGreater(len(counts), 1)

    def test_shortfalls(self):
        run, _ = run_once(build(spares=0, days=200), seed=1)
        self.assertGreater(run.failures["Spare"], 0)
        self.assertEqual(run.shortfalls["Spare"], run.failures["Spare"])


class TestMonteCarlo(unittest.TestCase):
    def test_matches_poisson(self):
        # 2 expected failures with 1 spare: P(shortfall) = 1 - 3 exp(-2)
        result = run_monte_carlo(build(spares=1), MonteCarloStudy(runs=400, seed=3))
        self.assertEqual(result.runs, 400)
        self.assertEqual(result.failed_runs, 0)
        (part,) = result.parts
        self.assertEqual(part.part, "Spare")
        self.assertEqual(part.elements, ["Plant"])
        self.assertAlmostEqual(part.expected, 2)
        self.assertAlmostEqual(part.mean, 2, delta=0.25)
        self.assertAlmostEqual(part.std, 2**0.5, delta=0.2)
        expected = poisson_shortfall_probability(2, 1)
        self.assertAlmostEqual(expected, 1 - 3 * 2.718281828**-2, places=6)
        self.assertAlmostEqual(part.shortfall_probability, expected, delta=0.08)
        self.assertAlmostEqual(result.shortfall_probability, expected, delta=0.08)
        self.assertEqual(sum(part.histogram), 400)
        self.assertLessEqual(part.percentiles["50"], part.percentiles["95"])
        # the mean shortfall is E[max(N - 1, 0)] = 2 - 1 + exp(-2)
        self.assertAlmostEqual(part.mean_shortfall, 1 + 2.718281828**-2, delta=0.25)

    def test_parallel_runs_match_sequential(self):
        scenario = build()
        study = MonteCarloStudy(runs=6, seed=11)
        sequential = run_monte_carlo(scenario, study)
        parallel = run_monte_carlo(scenario, study, workers=2)
        self.assertEqual(
            [r.failures for r in sequential.results],
            [r.failures for r in parallel.results],
        )

    def test_poisson_shortfall_probability(self):
        self.assertAlmostEqual(poisson_shortfall_probability(0.0, 0), 0.0)
        self.assertAlmostEqual(
            poisson_shortfall_probability(1.0, 0), 1 - 2.718281828**-1, places=6
        )


if __name__ == "__main__":
    unittest.main()
