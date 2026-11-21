"""
Tests of electrical power, energy storage, and surface mobility.
"""

import json
import unittest
from datetime import timedelta

from spacenet import schemas as s
from spacenet.simulation import (
    EventEvaluation,
    FullSimulator,
    PowerAnalysis,
    SimulationAnalysis,
)
from spacenet.simulation.records import PropellantFlowKind

from .util import ScenarioBuilder


def simulate(builder):
    """Simulates the scenario of a builder."""
    simulator = FullSimulator(builder.build())
    simulator.simulate()
    return simulator


def powered(builder, name, consumption=0.0, generation=0.0, solar=False, **kwargs):
    """Adds an element with one active state which uses power."""
    return builder.element(
        name,
        mass=kwargs.pop("mass", 100),
        states=[
            s.State(
                name="Operating",
                type="Active",
                power_consumption=consumption or None,
                power_generation=generation or None,
                generation_type="Solar" if solar else None,
            )
        ],
        current_state_index=0,
        **kwargs,
    )


def storage(capacity, charge=None):
    """Creates an energy storage."""
    return s.EnergyStorage(capacity=capacity, charge=charge)


def wait(builder, days, location=None):
    """Makes an event which advances time (creates a marker element)."""
    marker = builder.element(f"Marker {days}")
    return builder.create([marker], location or builder.lsp, days=days)


class TestPower(unittest.TestCase):
    def setUp(self):
        self.builder = ScenarioBuilder()

    def energy(self, sim, element):
        return sim.state.get_element(element.id).energy

    def test_constant_generation_charges_storage(self):
        b = self.builder
        reactor = powered(b, "Reactor", generation=10, energy_storage=storage(100, 0))
        b.mission([b.create([reactor], b.lsp), wait(b, 1)])
        sim = simulate(b)
        self.assertEqual(self.energy(sim, reactor), 100)
        self.assertEqual(sim.warnings, [])

    def test_solar_generation_scales_with_illumination(self):
        b = self.builder
        b.lsp.illumination = 0.5
        lander = powered(
            b,
            "Lander",
            consumption=4,
            generation=10,
            solar=True,
            energy_storage=storage(1000, 0),
        )
        b.mission([b.create([lander], b.lsp), wait(b, 10)])
        sim = simulate(b)
        # net 0.5 * 10 - 4 = 1 kW for 240 hours
        self.assertAlmostEqual(self.energy(sim, lander), 240)
        (record,) = [r for r in sim.power_records if r.name == "Lander"]
        self.assertEqual((record.generation, record.consumption), (5, 4))

    def test_deficit_warns_once(self):
        b = self.builder
        habitat = powered(b, "Habitat", consumption=5, energy_storage=storage(24))
        b.mission([b.create([habitat], b.lsp), wait(b, 1), wait(b, 2)])
        sim = simulate(b)
        self.assertEqual(self.energy(sim, habitat), 0)
        deficits = [r.deficit for r in sim.power_records]
        self.assertEqual(deficits, [96, 120])
        (warning,) = sim.warnings
        self.assertIn("Habitat at LSP has a power deficit of 96.0 kWh", warning.message)
        analysis = PowerAnalysis.create(sim)
        self.assertEqual(analysis.total_deficit, 216)
        (group,) = analysis.groups
        self.assertEqual(group.starts, [0, 1])
        self.assertEqual(group.ends, [1, 2])
        self.assertEqual(group.total_consumed, 240)

    def test_grid_connected_elements_share_power(self):
        for connected in (True, False):
            with self.subTest(connected=connected):
                b = ScenarioBuilder()
                reactor = powered(b, "Reactor", generation=40, grid_connected=True)
                habitat = powered(
                    b, "Habitat", consumption=30, grid_connected=connected
                )
                b.mission([b.create([reactor, habitat], b.lsp), wait(b, 1)])
                sim = simulate(b)
                names = sorted(r.name for r in sim.power_records)
                if connected:
                    self.assertEqual(names, ["LSP Grid"])
                    self.assertEqual(sim.power_records[0].deficit, 0)
                    self.assertEqual(sim.warnings, [])
                else:
                    self.assertEqual(names, ["Habitat", "LSP Grid"])
                    self.assertEqual(len(sim.warnings), 1)

    def test_carrier_powers_its_contents(self):
        b = self.builder
        lander = b.carrier("Lander")
        b.templates[-1].states = [
            s.State(name="Surface", type="Active", power_generation=2)
        ]
        b.templates[-1].current_state_index = 0
        b.templates[-1].energy_storage = storage(10)
        experiment = powered(b, "Experiment", consumption=1)
        b.mission(
            [
                b.create([lander], b.lsp),
                b.create([experiment], lander, location=b.lsp, priority=2),
                wait(b, 1),
            ]
        )
        sim = simulate(b)
        (record,) = sim.power_records
        self.assertEqual(record.name, "Lander")
        self.assertEqual(record.elements, ["Lander", "Experiment"])
        self.assertEqual(record.energy, 10)

    def test_no_power_constraint_on_earth(self):
        b = self.builder
        habitat = powered(b, "Habitat", consumption=5)
        b.mission([b.create([habitat], b.ksc), wait(b, 1, b.ksc)])
        sim = simulate(b)
        self.assertEqual(sim.power_records, [])

    def test_storage_must_survive_the_longest_night(self):
        b = self.builder
        b.lsp.max_night_duration = 100
        lander = powered(
            b,
            "Lander",
            consumption=2,
            generation=10,
            solar=True,
            energy_storage=storage(100),
        )
        b.mission([b.create([lander], b.lsp), wait(b, 1), wait(b, 20), wait(b, 31)])
        sim = simulate(b)
        # a stay shorter than a lunar day could be scheduled in sunlight
        (warning,) = sim.warnings
        self.assertEqual(warning.time, 31)
        self.assertIn(
            "requires 200.0 kWh to survive the longest night", warning.message
        )
        self.assertEqual(sim.power_records[0].night_energy, 200)
        self.assertEqual(
            [r.stays_overnight for r in sim.power_records], [False, False, True]
        )
        (group,) = PowerAnalysis.create(sim).groups
        self.assertTrue(group.night_shortfall)
        self.assertEqual(group.location_names, ["LSP", "LSP", "LSP"])

    def test_history_records_stored_energy(self):
        b = self.builder
        habitat = powered(b, "Habitat", consumption=1, energy_storage=storage(48))
        b.mission([b.create([habitat], b.lsp), wait(b, 1)])
        analysis = SimulationAnalysis.create(b.build())
        (element,) = [
            e
            for e in analysis.network_state(-1).locations[b.lsp.id]
            if e.name == "Habitat"
        ]
        self.assertEqual((element.energy, element.energy_capacity), (24, 48))
        self.assertEqual(analysis.totals.energy_deficit, 0)
        data = json.loads(analysis.model_dump_json(by_alias=True))
        self.assertEqual(data["power"]["groups"][0]["name"], "Habitat")


class TestSurfaceMobility(unittest.TestCase):
    def setUp(self):
        self.builder = ScenarioBuilder()

    def rover(self, speed=2, **kwargs):
        b = self.builder
        rover = b.add(
            s.SurfaceVehicle(
                name="Rover",
                mass=500,
                max_cargo_mass=100,
                max_crew=2,
                max_speed=10,
                fuel_tank=b.tank(100),
                **kwargs,
            ),
            s.InstSurfaceVehicle,
        )
        drive = s.SurfaceTransport(
            name="Drive",
            priority=2,
            mission_time=timedelta(days=1),
            location=b.lsp.id,
            edge=b.lsp_lsp2.id,
            vehicle=rover.id,
            speed=speed,
            duty_cycle=1,
        )
        b.mission([b.create([rover], b.lsp), drive])
        return rover

    def test_fuel_consumption(self):
        rover = self.rover(fuel_consumption=1)
        sim = simulate(self.builder)
        self.assertEqual(sim.errors, [])
        tank = sim.state.get_element(rover.id).fuel_tank
        self.assertAlmostEqual(tank.get_amount(tank.resource), 100 - 86.4)
        burned = [
            f for f in sim.propellant_flows if f.kind == PropellantFlowKind.BURNED
        ]
        self.assertAlmostEqual(burned[0].amount, 86.4)

    def test_insufficient_fuel(self):
        self.rover(fuel_consumption=2)
        sim = simulate(self.builder)
        self.assertIn(
            "requires 172.80 units of fuel to traverse 86.4 km but has 100.00",
            str(sim.spatial_errors[0]),
        )

    def test_energy_consumption(self):
        rover = self.rover(energy_consumption=1, energy_storage=storage(100))
        sim = simulate(self.builder)
        self.assertEqual(sim.errors, [])
        self.assertAlmostEqual(sim.state.get_element(rover.id).energy, 100 - 86.4)

    def test_insufficient_energy(self):
        self.rover(energy_consumption=1, energy_storage=storage(50))
        sim = simulate(self.builder)
        self.assertIn("requires 86.40 kWh to traverse", str(sim.spatial_errors[0]))
        self.assertEqual(
            sim.state.get_element(self.builder.instances[0].id).location.name, "LSP"
        )

    def test_max_speed_warning(self):
        self.rover(speed=5)
        sim = simulate(self.builder)
        self.assertEqual(sim.errors, [])
        self.assertIn(
            "travels at 18.0 km/h, above its maximum speed of 10.0 km/h",
            str(sim.warnings[0]),
        )

    def test_evaluate_traverse(self):
        self.rover(energy_consumption=0.5, energy_storage=storage(100))
        scenario = self.builder.build()
        evaluation = EventEvaluation.create(
            scenario, 0, scenario.mission_list[0].events[1], 1
        )
        transport = evaluation.transport
        self.assertAlmostEqual(transport.distance, 86.4)
        self.assertAlmostEqual(transport.speed, 7.2)
        self.assertEqual(transport.max_speed, 10)
        self.assertAlmostEqual(transport.energy_required, 43.2)
        self.assertEqual(transport.energy_available, 100)
        self.assertEqual(transport.fuel_required, 0)


class TestSchemas(unittest.TestCase):
    def test_defaults_are_omitted(self):
        element = s.Element(name="Element")
        data = element.model_dump(mode="json", by_alias=True, exclude_none=True)
        self.assertNotIn("energyStorage", data)
        self.assertNotIn("gridConnected", data)
        node = s.SurfaceNode(name="LSP", body_1="Moon", latitude=-89, longitude=0)
        data = node.model_dump(mode="json", by_alias=True, exclude_none=True)
        self.assertNotIn("illumination", data)
        state = s.State(name="Idle", type="Dormant")
        data = state.model_dump(mode="json", by_alias=True, exclude_none=True)
        self.assertEqual(set(data), {"id", "name", "type", "demandModels"})

    def test_invalid_values(self):
        with self.assertRaises(ValueError):
            s.SurfaceNode(
                name="LSP", body_1="Moon", latitude=-89, longitude=0, illumination=2
            )
        with self.assertRaises(ValueError):
            s.State(name="Ops", type="Active", power_consumption=-1)
        with self.assertRaises(ValueError):
            s.EnergyStorage(capacity=-1)
