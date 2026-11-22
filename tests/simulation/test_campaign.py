"""
Tests of campaign-scale analyses: cost, launch cadence, design life, and
the scenario end date.
"""

import unittest
from datetime import timedelta

from pydantic import ValidationError

from spacenet import schemas as s
from spacenet.simulation import (
    DemandSimulator,
    FullSimulator,
    PreSimulator,
    SimulationAnalysis,
)
from spacenet.simulation.analysis import CostAnalysis

from .util import START, ScenarioBuilder


def simulate(builder):
    """Simulates the scenario of a builder."""
    simulator = FullSimulator(builder.build())
    simulator.simulate()
    return simulator


class TestCost(unittest.TestCase):
    def setUp(self):
        b = self.builder = ScenarioBuilder()
        b.ksc_lsp.cost_per_transport = 150.0
        self.lander = b.carrier("Lander", mass=1000, unit_cost=500.0)
        self.payload = b.element("Payload", mass=100, unit_cost=20.0)
        b.mission(
            [
                b.create([self.lander], b.ksc),
                b.create([self.payload], self.lander, location=b.ksc, priority=2),
                b.flight([self.lander], b.ksc_lsp, priority=3),
            ],
            name="Delivery",
        )

    def test_costs_of_elements_and_transports(self):
        sim = simulate(self.builder)
        self.assertEqual(
            sorted((r.category, r.item, r.amount, r.mission) for r in sim.cost_records),
            [
                ("Element", "Lander", 500.0, "Delivery"),
                ("Element", "Payload", 20.0, "Delivery"),
                ("Transport", "KSC-LSP", 150.0, "Delivery"),
            ],
        )

    def test_elements_are_costed_once(self):
        b = self.builder
        # the lander flies back and again (two more transports)
        b.mission(
            [
                b.flight([self.lander], b.lsp_ksc, priority=1),
                b.flight([self.lander], b.ksc_lsp, days=4, priority=1),
            ],
            name="Reflight",
            days=5,
        )
        sim = simulate(b)
        analysis = CostAnalysis.create(sim, START)
        self.assertEqual(analysis.by_category, {"Element": 520.0, "Transport": 300.0})
        self.assertEqual(analysis.by_mission, {"Delivery": 670.0, "Reflight": 150.0})
        self.assertEqual(analysis.by_year, {2030: 820.0})
        self.assertEqual(analysis.total, 820.0)

    def test_instances_override_unit_cost(self):
        self.builder.instances[0].unit_cost = 450.0
        sim = simulate(self.builder)
        self.assertIn(450.0, [r.amount for r in sim.cost_records])

    def test_simulation_analysis_reports_cost(self):
        analysis = SimulationAnalysis.create(self.builder.build())
        self.assertEqual(analysis.totals.campaign_cost, 670.0)
        self.assertEqual(len(analysis.cost.items), 3)


class TestCadenceAndLife(unittest.TestCase):
    def test_departures_sooner_than_the_interval_warn(self):
        b = ScenarioBuilder()
        b.ksc_lsp.min_departure_interval = 10.0
        first, second = b.carrier("First"), b.carrier("Second")
        b.mission(
            [
                b.create([first, second], b.ksc),
                b.flight([first], b.ksc_lsp, days=0),
                b.flight([second], b.ksc_lsp, days=4),
            ]
        )
        sim = simulate(b)
        (warning,) = sim.warnings
        self.assertIn(
            "departs along KSC-LSP 4.0 days after the previous transport "
            "(minimum interval 10.0 days)",
            str(warning),
        )

    def test_elements_beyond_design_life_warn(self):
        b = ScenarioBuilder()
        habitat = b.element("Habitat", design_life=1.0)
        marker = b.element("Marker")
        b.mission(
            [
                b.create([habitat], b.lsp),
                s.CreateElements(
                    name="Later",
                    priority=1,
                    mission_time=timedelta(days=400),
                    location=b.lsp.id,
                    container=b.lsp.id,
                    elements=[marker.id],
                ),
            ]
        )
        sim = simulate(b)
        (warning,) = sim.warnings
        self.assertIn(
            "Habitat is used beyond its design life of 1.0 years", str(warning)
        )
        self.assertEqual(sim.state.get_element(habitat.id).created_time, 0)


def water_habitat(builder, name="Habitat", rate=1.0, **kwargs):
    """Adds a habitat which demands water (kg/day) while active."""
    model = s.RatedDemandModel(
        name="Water",
        demands=[
            s.GenericResourceAmountRate(
                class_of_supply=201, environment="Pressurized", rate=rate
            )
        ],
    )
    builder.demand_models.append(model)
    state = s.State(
        name="Active",
        type="Active",
        demand_models=[s.InstRatedDemandModel(name="Water", template_id=model.id)],
        **kwargs,
    )
    return builder.carrier(name, states=[state], current_state_index=0)


def demand_mass(simulator):
    """Gets the total mass (kg) of the unsatisfied demands of a simulation."""
    return sum(d.demands.total_mass for d in simulator.unsatisfied_demands)


class TestEndDate(unittest.TestCase):
    def setUp(self):
        b = self.builder = ScenarioBuilder()
        self.habitat = water_habitat(b)
        b.mission([b.create([self.habitat], b.lsp)], name="Outpost")

    def simulate(self, cls=DemandSimulator, days=None, **kwargs):
        if days is not None:
            self.builder.end_date = START + timedelta(days=days)
        simulator = cls(self.builder.build(), **kwargs)
        simulator.simulate()
        return simulator

    def test_without_an_end_date_demands_stop_at_the_last_event(self):
        sim = self.simulate(demands_satisfied=False)
        self.assertIsNone(sim.end_time)
        self.assertEqual(sim.time, 0)
        self.assertEqual(demand_mass(sim), 0)

    def test_demands_continue_to_the_end_date(self):
        sim = self.simulate(days=365, demands_satisfied=False)
        self.assertEqual(sim.end_time, 365)
        self.assertEqual(sim.time, 365)
        self.assertEqual(sim.warnings, [])
        self.assertEqual(
            [(d.time, d.demands.total_mass) for d in sim.unsatisfied_demands],
            [(365, 365)],
        )

    def test_events_after_the_end_date_are_not_simulated(self):
        b = self.builder
        late = b.element("Late")
        b.mission([b.create([late], b.lsp)], name="Resupply", days=400)
        sim = self.simulate(days=365, demands_satisfied=False)
        self.assertEqual(sim.time, 365)
        self.assertIsNone(sim.state.get_element(late.id).location)
        self.assertEqual(demand_mass(sim), 365)
        (warning,) = sim.warnings
        self.assertEqual(warning.time, 365)
        self.assertEqual(
            warning.message,
            "Events of Resupply after the scenario end date are not simulated.",
        )

    def test_events_at_the_end_date_are_simulated(self):
        b = self.builder
        late = b.element("Late")
        b.mission([b.create([late], b.lsp)], name="Resupply", days=365)
        sim = self.simulate(days=365)
        self.assertEqual(sim.state.get_element(late.id).location.name, "LSP")
        self.assertEqual(sim.warnings, [])

    def test_transports_in_progress_at_the_end_date_do_not_arrive(self):
        b = self.builder
        lander = b.carrier("Lander")
        b.mission(
            [b.create([lander], b.ksc), b.flight([lander], b.ksc_lsp)],
            name="Delivery",
            days=364,
        )
        sim = self.simulate(days=365)
        self.assertEqual(sim.state.get_element(lander.id).location.name, "KSC-LSP")
        (warning,) = sim.warnings
        self.assertIn("Events of Delivery after", warning.message)

    def test_final_demands_are_aggregated_to_the_last_arrival(self):
        b = ScenarioBuilder()
        habitat = water_habitat(b)
        b.mission(
            [b.create([habitat], b.ksc), b.flight([habitat], b.ksc_lsp)],
            name="Outpost",
        )
        b.end_date = START + timedelta(days=100)
        sim = DemandSimulator(b.build(), demands_satisfied=False)
        sim.simulate()
        ((point, node_demands),) = sim.aggregated_node_demands
        ((edge, edge_demands),) = sim.aggregated_edge_demands
        self.assertEqual((point.node.name, point.time), ("LSP", 3))
        # 3 days in transit and 97 days on the surface
        self.assertAlmostEqual(edge_demands.total_mass, 3)
        self.assertAlmostEqual(node_demands.total_mass, 97)
        self.assertEqual(edge.edge.name, "KSC-LSP")
        self.assertEqual(sim.unassigned_demands, [])

    def test_full_simulator_measures_the_final_interval(self):
        b = self.builder
        crew = b.crew("Crew")
        b.missions[0].events.append(b.create([crew], self.habitat, location=b.lsp))
        sim = self.simulate(FullSimulator, days=10)
        self.assertEqual(sim.network_history[-1].time, 10)
        self.assertEqual(sim.total_crew_surface_days, 10)
        self.assertEqual(sim.total_crew_time, 10 * 24)
        analysis = SimulationAnalysis.create(b.build())
        self.assertEqual(analysis.end_time, 10)
        # the timeline of the browser interface extends to the end date
        self.assertEqual(analysis.history.frames[-1].time, 10)

    def test_power_is_balanced_to_the_end_date(self):
        b = ScenarioBuilder()
        habitat = water_habitat(b, power_generation=5.0, power_consumption=2.0)
        b.mission([b.create([habitat], b.lsp)])
        b.end_date = START + timedelta(days=30)
        sim = FullSimulator(b.build())
        sim.simulate()
        (record,) = sim.power_records
        self.assertEqual((record.time, record.duration), (30, 30))

    def test_pre_simulator_runs_to_the_end_date(self):
        b = self.builder
        late = b.element("Late")
        b.mission([b.create([late], b.lsp)], name="Resupply", days=400)
        sim = self.simulate(PreSimulator, days=365, demands_satisfied=False)
        self.assertEqual(sim.time, 365)
        self.assertEqual(demand_mass(sim), 365)
        self.assertIsNone(sim.state.get_element(late.id).location)
        # a specified time may be after the end date (to inspect an event)
        sim.simulate(400, priority=1)
        self.assertEqual(sim.time, 400)

    def test_end_date_must_be_after_the_start_date(self):
        self.builder.end_date = START
        with self.assertRaisesRegex(ValidationError, "end date must be after"):
            self.builder.build()

    def test_end_date_is_serialized(self):
        self.builder.end_date = START + timedelta(days=30)
        data = self.builder.build().model_dump(mode="json", by_alias=True)
        self.assertEqual(data["endDate"], "2030-01-31T00:00:00Z")
        self.assertEqual(
            s.Scenario.model_validate(data).end_date, self.builder.end_date
        )
