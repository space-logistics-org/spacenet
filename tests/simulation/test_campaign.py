"""
Tests of campaign-scale analyses: cost, launch cadence, and design life.
"""

import unittest
from datetime import timedelta

from spacenet import schemas as s
from spacenet.simulation import FullSimulator, SimulationAnalysis
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
