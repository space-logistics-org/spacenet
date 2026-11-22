"""
Tests of time-phased crew consumables.
"""

import unittest

from spacenet import schemas as s
from spacenet.simulation import DemandsAnalysis, FullSimulator

from .util import ScenarioBuilder, load_scenario


def build(time_phased=True, transit_demands_omitted=False, launch_day=2):
    """
    Builds a mission in which two crew members wait at KSC, fly to LSP
    (3 days), stay 5 days, and fly back (3 days).
    """
    b = ScenarioBuilder(time_phased_consumables=time_phased)
    model = s.CrewConsumablesDemandModel(
        name="Consumables",
        water_recovery_rate=0.0,
        reserves_duration=2.0,
        transit_demands_omitted=transit_demands_omitted,
    )
    b.demand_models.append(model)
    lander = b.carrier("Lander", mass=1000, max_crew=2)
    crew = [b.crew("A"), b.crew("B")]
    flight = b.flight([lander], b.ksc_lsp, days=launch_day, priority=3)
    back = b.flight([lander], b.lsp_ksc, days=launch_day + 8, priority=1)
    b.mission(
        [
            b.create([lander], b.ksc),
            b.create(crew, lander, location=b.ksc, priority=2),
            flight,
            back,
        ],
        demand_models=[
            s.InstCrewConsumablesDemandModel(name="Consumables", template_id=model.id)
        ],
        return_origin=b.lsp.id,
        return_destination=b.ksc.id,
    )
    return b


def demand_mass(simulator, location=None):
    """Sums the unsatisfied demands (at a location)."""
    return sum(
        d.demands.total_mass
        for d in simulator.unsatisfied_demands
        if location is None or d.location.name == location
    )


class TestTimePhasedConsumables(unittest.TestCase):
    def simulate(self, builder):
        simulator = FullSimulator(builder.build())
        simulator.simulate()
        self.assertEqual(simulator.spatial_errors, [])
        return simulator

    def test_total_matches_lumped_demands(self):
        lumped = self.simulate(build(time_phased=False, launch_day=0))
        phased = self.simulate(build(launch_day=0))
        self.assertEqual(len(lumped.unsatisfied_demands), 1)
        self.assertGreater(len(phased.unsatisfied_demands), 3)
        self.assertAlmostEqual(demand_mass(phased), demand_mass(lumped), delta=0.5)

    def test_lumped_demands_count_waiting_on_earth(self):
        # lumped demands count transit from the start of the mission, including
        # the days which the crew waits on Earth before launch
        lumped = self.simulate(build(time_phased=False, launch_day=2))
        phased = self.simulate(build(launch_day=2))
        daily = phased.state.missions[0].demand_models[0].daily_demands(1)
        self.assertGreater(
            demand_mass(lumped), demand_mass(phased) + 3 * daily.total_mass
        )

    def test_demands_where_and_when_the_crew_is(self):
        phased = self.simulate(build())
        model = phased.state.missions[0].demand_models[0]
        times = sorted({round(d.time, 3) for d in phased.unsatisfied_demands})
        # no demands while the crew waits at KSC before launch (demands are
        # recorded at the end of each interval, i.e., on arrival at LSP)
        self.assertEqual(times[0], 5)
        self.assertEqual(times[-1], 13)
        daily = model.daily_demands(1).total_mass
        # two crew in transit for 3 days each way and on the surface for 5
        self.assertAlmostEqual(demand_mass(phased, "LSP"), 2 * 5 * daily, places=1)
        self.assertAlmostEqual(
            demand_mass(phased, "KSC-LSP"),
            2 * 3 * daily
            + model.crew_demands(2).total_mass
            + model.mission_demands().total_mass,
            places=1,
        )
        self.assertAlmostEqual(demand_mass(phased, "LSP-KSC"), 2 * 3 * daily, places=1)

    def test_launch_date_does_not_change_demands(self):
        early = self.simulate(build(launch_day=0))
        late = self.simulate(build(launch_day=20))
        self.assertAlmostEqual(demand_mass(early), demand_mass(late), places=6)

    def test_transit_demands_omitted(self):
        phased = self.simulate(build(transit_demands_omitted=True))
        model = phased.state.missions[0].demand_models[0]
        # carried items are demanded on departure; daily demands only on the surface
        self.assertAlmostEqual(
            demand_mass(phased, "LSP"),
            2 * 5 * model.daily_demands(1).total_mass,
            places=1,
        )
        self.assertAlmostEqual(demand_mass(phased, "LSP-KSC"), 0.0, places=6)

    def test_demands_are_manifested(self):
        simulator = DemandsAnalysis.simulate(build().build())
        self.assertGreater(len(simulator.unsatisfied_demands), 3)
        self.assertTrue(simulator.supply_edges)


class TestCampaignConsumables(unittest.TestCase):
    def test_artemis_ii_flyby(self):
        simulator = FullSimulator(load_scenario("artemis/artemis_add_campaign.json"))
        simulator.simulate()
        mission = next(m for m in simulator.state.missions if m.name == "Artemis II")
        model = mission.demand_models[0]
        demands = [
            d
            for d in simulator.unsatisfied_demands
            if d.event is not None and d.event.name == f"Crew Consumables for {mission}"
        ]
        # four crew for a 10-day flyby with carried items, reserves, and equipment
        expected = (
            model.daily_demands(4 * 10).total_mass
            + model.crew_demands(4).total_mass
            + model.mission_demands().total_mass
        )
        self.assertAlmostEqual(
            sum(d.demands.total_mass for d in demands), expected, delta=1
        )
        self.assertLess(expected, 1_100)
