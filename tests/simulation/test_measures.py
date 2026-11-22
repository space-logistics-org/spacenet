"""
Tests of the campaign measures of effectiveness: the mass launched per mass
landed, the logistics mass per crew-day, the days of supply on hand, and the
Earth independence.
"""

import math
import unittest
from datetime import timedelta

from spacenet import schemas as s
from spacenet.simulation import FullSimulator, SimulationAnalysis
from spacenet.simulation.records import SOURCE_EARTH, SOURCE_IN_SITU
from spacenet.trades import evaluate, metric_names

from .util import ScenarioBuilder


def simulate(builder):
    """Simulates the scenario of a builder."""
    simulator = FullSimulator(builder.build())
    simulator.simulate()
    return simulator


def rated(builder, demands):
    """Adds an element at a state which demands resources at constant rates."""
    model = s.RatedDemandModel(
        name="Rated",
        demands=[
            s.ResourceAmountRate(resource=resource.id, rate=rate)
            for resource, rate in demands
        ],
    )
    builder.demand_models.append(model)
    return builder.element(
        "Habitat",
        mass=1000,
        states=[
            s.State(
                name="Active",
                type="Active",
                demand_models=[
                    s.InstRatedDemandModel(name="Rated", template_id=model.id)
                ],
            )
        ],
        current_state_index=0,
    )


def supplies(builder, resource, amount, name="Supplies"):
    """Adds a container of a resource."""
    return builder.container(
        name,
        max_cargo_mass=1000,
        contents=[s.ResourceAmount(resource=resource.id, amount=amount)],
    )


class TestLandedMass(unittest.TestCase):
    """Mass landed on bodies other than Earth and the mass launched per mass landed."""

    def test_flight(self):
        b = ScenarioBuilder()
        lander = b.carrier("Lander", mass=1000)
        crew = [b.crew("A"), b.crew("B")]
        b.mission(
            [
                b.create([lander], b.ksc),
                b.create(crew, lander, location=b.ksc, priority=2),
                b.flight([lander], b.ksc_lsp, priority=3),
                b.flight([lander], b.lsp_ksc, days=10),
            ]
        )
        sim = simulate(b)
        # the return to Earth does not land
        (landing,) = sim.landed_mass_history
        self.assertEqual(landing.time, 3)
        self.assertEqual(landing.location.name, "LSP")
        self.assertAlmostEqual(landing.amount, 1200)
        self.assertAlmostEqual(sim.total_launch_mass, 1200)
        self.assertAlmostEqual(sim.total_launch_mass_per_landed_mass, 1)

    def test_space_transport_lands_mass_after_burns(self):
        b = ScenarioBuilder()
        descent = s.Burn(time=timedelta(0), delta_v=1000)
        edge = s.SpaceEdge(
            name="LEO-LSP",
            origin=b.leo.id,
            destination=b.lsp.id,
            duration=timedelta(days=4),
            burns=[descent],
        )
        stage = b.vehicle("Lander", mass=1000, fuel=9000, isp=300)
        b.mission(
            [
                b.create([stage], b.leo),
                s.SpaceTransport(
                    name="Descent",
                    priority=2,
                    mission_time=timedelta(0),
                    location=b.leo.id,
                    edge=edge.id,
                    elements=[stage.id],
                    burn_stage_sequence=[
                        s.BurnStageSequence(
                            burn=descent.id,
                            actions=[s.BurnStageItem(element=stage.id, type="Burn")],
                        )
                    ],
                ),
            ]
        )
        scenario = b.build()
        scenario.network.edges.append(edge)
        sim = FullSimulator(scenario)
        sim.simulate()
        (landing,) = sim.landed_mass_history
        self.assertEqual(landing.time, 4)
        final = sim.state.get_element(stage.id).total_mass
        self.assertLess(final, 10000)
        self.assertAlmostEqual(landing.amount, final)
        # nothing is launched from Earth
        self.assertEqual(sim.total_launch_mass_per_landed_mass, 0)

    def test_no_landing(self):
        b = ScenarioBuilder()
        b.mission([b.create([b.element()], b.lsp)])
        sim = simulate(b)
        self.assertEqual(sim.total_landed_mass, 0)
        self.assertEqual(sim.total_launch_mass_per_landed_mass, 0)


class TestLogistics(unittest.TestCase):
    """
    Two crew members live in a habitat on the Moon for 10 days; it demands
    2 kg/day of water (and spares, which are discrete) with 40 kg of water
    on hand.
    """

    def scenario(self, water=40.0):
        b = ScenarioBuilder()
        habitat = rated(b, [(b.water, 2), (b.spare, 0.5)])
        b.mission(
            [
                b.create([habitat, supplies(b, b.water, water)], b.lsp),
                b.create([b.crew("A"), b.crew("B")], b.lsp),
                b.create([b.element("Marker 5")], b.lsp, days=5),
                b.create([b.element("Marker 10")], b.lsp, days=10),
            ]
        )
        return simulate(b)

    def test_logistics_mass_per_crew_day(self):
        sim = self.scenario()
        self.assertAlmostEqual(sim.total_crew_days, 20)
        # 20 kg of water and 5 spares of 5 kg
        self.assertAlmostEqual(sim.total_logistics_mass, 45)
        self.assertAlmostEqual(sim.total_logistics_mass_per_crew_day, 2.25)

    def test_days_of_supply(self):
        sim = self.scenario()
        # discrete resources (spares) are excluded
        self.assertEqual(
            [
                (m.time, m.location.name, m.amount, m.type)
                for m in sim.days_of_supply_history
            ],
            [(5, "LSP", 15, "Water"), (10, "LSP", 10, "Water")],
        )
        self.assertEqual(sim.min_days_of_supply, 10)

    def test_days_of_supply_run_out(self):
        sim = self.scenario(water=15)
        self.assertEqual([m.amount for m in sim.days_of_supply_history], [2.5, 0])
        # demands count whether or not they are satisfied
        self.assertAlmostEqual(sim.total_logistics_mass, 45)
        self.assertAlmostEqual(
            sum(m.amount for m in sim.consumption_history if m.resource == "Water"), 15
        )

    def test_crew_days_exclude_earth_surface(self):
        b = ScenarioBuilder()
        lander = b.carrier("Lander", mass=1000)
        b.mission(
            [
                b.create([lander], b.ksc),
                b.create([b.crew("A")], lander, location=b.ksc, priority=2),
                b.flight([lander], b.ksc_lsp, days=4, priority=3),
                b.flight([lander], b.lsp_ksc, days=10),
                b.create([b.element("Marker")], b.ksc, days=20),
            ]
        )
        sim = simulate(b)
        # 3 days on each flight and 3 days on the Moon
        self.assertAlmostEqual(sim.total_crew_days, 9)
        self.assertAlmostEqual(sim.total_crew_time, 20 * 24)

    def test_no_demands(self):
        b = ScenarioBuilder()
        b.mission(
            [b.create([b.crew("A")], b.lsp), b.create([b.element()], b.lsp, days=2)]
        )
        sim = simulate(b)
        self.assertEqual(sim.total_logistics_mass_per_crew_day, 0)
        self.assertIsNone(sim.min_days_of_supply)


class TestEarthIndependence(unittest.TestCase):
    """
    A plant on the Moon electrolyzes water to oxygen (8 kg/day, modeled by the
    oxidizer resource) and hydrogen (1 kg/day) for 10 days while a habitat
    demands 4 kg/day of oxygen and 1 kg/day of water delivered from Earth.
    """

    def setUp(self):
        b = self.builder = ScenarioBuilder()
        process = s.ISRUProcessDemandModel(
            name="Electrolysis",
            inputs=[s.ResourceAmountRate(resource=b.water.id, rate=9)],
            outputs=[
                s.ResourceAmountRate(resource=b.oxidizer.id, rate=8),
                s.ResourceAmountRate(resource=b.fuel.id, rate=1),
            ],
        )
        b.demand_models.append(process)
        self.plant = b.element(
            "Plant",
            states=[
                s.State(
                    name="Operating",
                    type="Active",
                    demand_models=[
                        s.InstISRUProcessDemandModel(
                            name=process.name, template_id=process.id
                        )
                    ],
                )
            ],
            current_state_index=0,
        )
        self.elements = [
            self.plant,
            supplies(b, b.water, 200, "Water Tank"),
            supplies(b, b.oxidizer, 0, "Oxygen Tank"),
            supplies(b, b.fuel, 0, "Hydrogen Tank"),
            rated(b, [(b.oxidizer, 4), (b.water, 1)]),
        ]

    def test_in_situ_consumption(self):
        b = self.builder
        b.mission(
            [
                b.create(self.elements, b.lsp),
                b.create([b.element("Marker")], b.lsp, days=10),
            ]
        )
        sim = simulate(b)
        sources = {(m.resource, m.type): m.amount for m in sim.consumption_history}
        self.assertEqual(
            {k: round(v, 6) for k, v in sources.items()},
            {("Oxidizer", SOURCE_IN_SITU): 40, ("Water", SOURCE_EARTH): 10},
        )
        self.assertAlmostEqual(sim.total_consumption, 50)
        self.assertAlmostEqual(sim.total_in_situ_consumption, 40)
        self.assertAlmostEqual(sim.total_earth_independence, 0.8)

    def test_burns(self):
        b = self.builder
        lunar = b.vehicle("Lunar Stage", mass=1000, fuel=100)
        orbital = b.vehicle("Orbital Stage", mass=1000, fuel=100)
        b.mission(
            [
                b.create(self.elements + [lunar], b.lsp),
                b.create([orbital], b.leo),
                # 10 kg of hydrogen are produced before the lunar burn
                b.burn_event([lunar], location=b.lsp, days=10),
                # burns in Earth orbit are not counted
                b.burn_event([orbital], location=b.leo, days=10),
            ]
        )
        sim = simulate(b)
        burned = 100 - sim.state.get_element(lunar.id).fuel_tank.amount
        self.assertGreater(burned, 10)
        fuel = {
            m.type: m.amount for m in sim.consumption_history if m.resource == "Fuel"
        }
        self.assertAlmostEqual(fuel[SOURCE_IN_SITU], 10)
        self.assertAlmostEqual(fuel[SOURCE_EARTH], burned - 10)
        self.assertAlmostEqual(sim.total_consumption, 50 + burned)
        self.assertAlmostEqual(sim.total_in_situ_consumption, 50)

    def test_without_isru(self):
        b = ScenarioBuilder()
        habitat = rated(b, [(b.water, 1)])
        b.mission(
            [
                b.create([habitat, supplies(b, b.water, 100)], b.lsp),
                b.create([b.element("Marker")], b.lsp, days=10),
            ]
        )
        sim = simulate(b)
        self.assertAlmostEqual(sim.total_consumption, 10)
        self.assertEqual(sim.total_earth_independence, 0)


class TestAnalysis(unittest.TestCase):
    """Reports of the measures in the simulation analysis and trade studies."""

    def scenario(self):
        b = ScenarioBuilder()
        habitat = rated(b, [(b.water, 2)])
        b.mission(
            [
                b.create([habitat, supplies(b, b.water, 40), b.crew("A")], b.lsp),
                b.create([b.element("Marker 5")], b.lsp, days=5),
                b.create([b.element("Marker 10")], b.lsp, days=10),
            ]
        )
        return b.build()

    def test_totals_and_histories(self):
        analysis = SimulationAnalysis.create(self.scenario())
        totals = analysis.totals
        self.assertAlmostEqual(totals.crew_days, 10)
        self.assertAlmostEqual(totals.logistics_mass, 20)
        self.assertAlmostEqual(totals.logistics_mass_per_crew_day, 2)
        self.assertAlmostEqual(totals.consumption_mass, 20)
        self.assertEqual(totals.earth_independence, 0)
        self.assertEqual(totals.min_days_of_supply, 10)
        measures = analysis.measures
        self.assertEqual([m.amount for m in measures.days_of_supply], [15, 10])
        self.assertEqual({m.type for m in measures.days_of_supply}, {"Water"})
        self.assertEqual({m.type for m in measures.consumption}, {SOURCE_EARTH})
        # records of one time and location are aggregated
        self.assertEqual([m.amount for m in measures.crew_days], [5, 5])
        self.assertEqual([m.amount for m in measures.logistics_mass], [10, 10])
        data = analysis.model_dump(by_alias=True)
        self.assertIn("minDaysOfSupply", data["totals"])
        self.assertIn("daysOfSupply", data["measures"])

    def test_trade_metrics(self):
        names = metric_names()
        for name in (
            "landedMass",
            "launchMassPerLandedMass",
            "logisticsMassPerCrewDay",
            "earthIndependence",
            "minDaysOfSupply",
        ):
            self.assertIn(name, names)
        metrics = evaluate(self.scenario())
        self.assertEqual(metrics["minDaysOfSupply"], 10)
        b = ScenarioBuilder()
        b.mission([b.create([b.element()], b.lsp)])
        self.assertTrue(math.isnan(evaluate(b.build())["minDaysOfSupply"]))


if __name__ == "__main__":
    unittest.main()
