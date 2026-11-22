"""
Tests of the maximum time step, which divides long intervals between events
into time steps.
"""

import unittest
from datetime import timedelta

from pydantic import ValidationError

from spacenet import schemas as s
from spacenet.simulation import (
    AggregatedDemandsAnalysis,
    DemandSimulator,
    FullSimulator,
    MiniSimulator,
    PreSimulator,
)

from .test_measures import rated, supplies
from .util import START, ScenarioBuilder, load_scenario


class TestTimeStep(unittest.TestCase):
    """
    A habitat on the Moon demands 2 kg/day of water from 40 kg on hand
    between events at days 0 and 10 (and 5, if not skipped).
    """

    def scenario(self, step=None, middle=True, end=None, water=40, flight=False):
        b = ScenarioBuilder(max_time_step=step)
        events = []
        if flight:
            # a flight arrives at the Moon at day 3 (a supply point)
            lander = b.carrier("Lander")
            events += [b.create([lander], b.ksc), b.flight([lander], b.ksc_lsp)]
        events += [
            b.create(
                [rated(b, [(b.water, 2)]), supplies(b, b.water, water), b.crew("A")],
                b.lsp,
            ),
            b.create([b.element("Marker 10")], b.lsp, days=10),
        ]
        if middle:
            events.append(b.create([b.element("Marker 5")], b.lsp, days=5))
        b.mission(events)
        if end is not None:
            b.end_date = START + timedelta(days=end)
        return b.build()

    def simulate(self, scenario, cls=FullSimulator):
        simulator = cls(scenario)
        simulator.simulate()
        return simulator

    def test_steps_between_events(self):
        sim = self.simulate(self.scenario(step=2))
        # steps at 2 and 4 before the event at 5, then at 7 and 9
        self.assertEqual(
            [round(m.time, 6) for m in sim.days_of_supply_history], [2, 4, 5, 7, 9, 10]
        )
        self.assertEqual(
            [round(m.amount, 6) for m in sim.days_of_supply_history],
            [18, 16, 15, 13, 11, 10],
        )
        self.assertEqual(
            # before and after the events at the start
            [round(f.time, 6) for f in sim.network_history.frames],
            [0, 0, 2, 4, 5, 7, 9, 10],
        )
        self.assertAlmostEqual(sim.total_logistics_mass, 20)
        self.assertAlmostEqual(sim.total_crew_days, 10)

    def test_without_steps(self):
        sim = self.simulate(self.scenario(middle=False))
        self.assertEqual([m.time for m in sim.days_of_supply_history], [10])

    def test_exact_multiple(self):
        # no step coincides with an event
        sim = self.simulate(self.scenario(step=5, middle=False))
        self.assertEqual([m.time for m in sim.days_of_supply_history], [5, 10])

    def test_steps_to_end_date(self):
        sim = self.simulate(self.scenario(step=3, middle=False, end=20))
        self.assertEqual(
            [round(m.time, 6) for m in sim.days_of_supply_history],
            [3, 6, 9, 10, 13, 16, 19, 20],
        )
        self.assertEqual(sim.time, 20)
        # the water runs out at day 20
        self.assertAlmostEqual(sim.days_of_supply_history[-1].amount, 0)

    def test_simulators_agree(self):
        scenario = self.scenario(step=2, end=20)
        reference = self.simulate(self.scenario(end=20), DemandSimulator)
        demand = self.simulate(scenario, DemandSimulator)
        full = self.simulate(scenario)
        mini = self.simulate(scenario, MiniSimulator)
        for sim in (demand, full, mini):
            self.assertEqual(sim.time, 20)
        # water runs out at day 20 with or without steps
        for sim in (reference, demand, full):
            self.assertEqual(sim.unsatisfied_demands, [])
        self.assertEqual(
            sorted({round(s.time, 6) for s in mini.location_history}),
            [0, 2, 4, 5, 7, 9, 10, 12, 14, 16, 18, 20],
        )

    def test_pre_simulator(self):
        sim = PreSimulator(self.scenario(step=2))
        sim.simulate(time=8.5)
        self.assertEqual(sim.time, 8.5)
        (supply,) = [e for e in sim.state.network.elements if e.name == "Supplies"]
        self.assertAlmostEqual(next(iter(supply.contents.values())), 40 - 17)

    def test_aggregated_demands(self):
        # 10 kg of water on hand for 20 kg of demands
        reference = self.simulate(self.scenario(water=10, flight=True), DemandSimulator)
        stepped = self.simulate(
            self.scenario(step=2, water=10, flight=True), DemandSimulator
        )
        # demands are divided among more events but aggregate to the same
        # supply points
        self.assertEqual(
            [round(d.time, 6) for d in reference.unsatisfied_demands], [10]
        )
        self.assertEqual(
            # the water runs out at day 5
            [round(d.time, 6) for d in stepped.unsatisfied_demands],
            [7, 9, 10],
        )
        expected = AggregatedDemandsAnalysis.create(reference).nodes
        actual = AggregatedDemandsAnalysis.create(stepped).nodes
        self.assertEqual(
            [round(n.total_consumption_mass, 6) for n in expected],
            [round(n.total_consumption_mass, 6) for n in actual],
        )
        self.assertAlmostEqual(sum(n.total_consumption_mass for n in actual), 10)

    def test_reference_scenarios(self):
        for path in (
            "quick_start/completed_quick_start_2_w_db.json",
            "artemis/artemis_add_campaign.json",
        ):
            scenario = load_scenario(path)
            reference = FullSimulator(scenario)
            reference.simulate()
            scenario.configuration.max_time_step = 7
            stepped = FullSimulator(scenario)
            stepped.simulate()
            with self.subTest(path):
                self.assertGreater(
                    len(stepped.network_history), len(reference.network_history)
                )
                for measure in (
                    "total_crew_time",
                    "total_launch_mass",
                    "total_logistics_mass",
                    "total_consumption",
                ):
                    self.assertAlmostEqual(
                        getattr(stepped, measure), getattr(reference, measure), 6
                    )
                self.assertEqual(
                    len(stepped.unsatisfied_demands),
                    len(reference.unsatisfied_demands),
                )

    def test_positive(self):
        with self.assertRaises(ValidationError):
            s.Configuration(max_time_step=0)
        self.assertIsNone(s.Configuration().max_time_step)


if __name__ == "__main__":
    unittest.main()
