"""
Tests of in-situ resource utilization (ISRU) processes.
"""

import unittest

from pydantic import ValidationError

from spacenet import schemas as s
from spacenet.simulation import (
    FullSimulator,
    ISRUAnalysis,
    PropellantAnalysis,
    SimulationAnalysis,
)
from spacenet.simulation.records import PropellantFlowKind

from .util import ScenarioBuilder


def simulate(builder):
    """Simulates the scenario of a builder."""
    simulator = FullSimulator(builder.build())
    simulator.simulate()
    return simulator


class TestISRU(unittest.TestCase):
    """
    A plant electrolyzes water (9 kg/day) to oxygen (8 kg/day, modeled by the
    oxidizer resource) and hydrogen (1 kg/day, modeled by the fuel resource)
    with 2 kW at its full rate.
    """

    def setUp(self):
        b = self.builder = ScenarioBuilder()
        self.process = s.ISRUProcessDemandModel(
            name="Electrolysis",
            inputs=[s.ResourceAmountRate(resource=b.water.id, rate=9)],
            outputs=[
                s.ResourceAmountRate(resource=b.oxidizer.id, rate=8),
                s.ResourceAmountRate(resource=b.fuel.id, rate=1),
            ],
            power=2,
        )
        b.demand_models.append(self.process)

    def plant(self, generation=10.0, consumption=0.0, process=None):
        """Adds a plant which operates the process in its active state."""
        process = process or self.process
        return self.builder.element(
            "Plant",
            mass=100,
            states=[
                s.State(
                    name="Operating",
                    type="Active",
                    power_generation=generation or None,
                    power_consumption=consumption or None,
                    demand_models=[
                        s.InstISRUProcessDemandModel(
                            name=process.name, template_id=process.id
                        )
                    ],
                )
            ],
            current_state_index=0,
        )

    def storage(self, water=100.0, oxygen_capacity=1000.0, hydrogen_capacity=1000.0):
        """Adds containers of water, oxygen, and hydrogen."""
        b = self.builder
        return [
            b.container(
                "Water Tank",
                max_cargo_mass=1000,
                contents=[s.ResourceAmount(resource=b.water.id, amount=water)],
            ),
            b.container(
                "Oxygen Tank",
                max_cargo_mass=oxygen_capacity,
                contents=[s.ResourceAmount(resource=b.oxidizer.id, amount=0)],
            ),
            b.container(
                "Hydrogen Tank",
                max_cargo_mass=hydrogen_capacity,
                contents=[s.ResourceAmount(resource=b.fuel.id, amount=0)],
            ),
        ]

    def operate(self, elements, days=10):
        """Creates elements at the lunar surface and waits a number of days."""
        b = self.builder
        marker = b.element("Marker")
        b.mission([b.create(elements, b.lsp), b.create([marker], b.lsp, days=days)])
        return simulate(b)

    def amounts(self, sim, element):
        return {
            r.name: round(a, 6)
            for r, a in sim.state.get_element(element.id).contents.items()
        }

    def test_full_rate(self):
        water, oxygen, hydrogen = self.storage()
        sim = self.operate([self.plant(), water, oxygen, hydrogen])
        self.assertEqual(self.amounts(sim, water), {"Water": 10})
        self.assertEqual(self.amounts(sim, oxygen), {"Oxidizer": 80})
        self.assertEqual(self.amounts(sim, hydrogen), {"Fuel": 10})
        (record,) = sim.isru_records
        self.assertEqual(record.rate, 1)
        self.assertIsNone(record.limit)
        self.assertEqual(record.power, 2)
        self.assertAlmostEqual(record.energy, 480)
        self.assertAlmostEqual(record.input_mass, 90)
        self.assertAlmostEqual(record.output_mass, 90)
        self.assertEqual(sim.warnings, [])
        # the process power is part of the energy balance of the plant
        (power,) = [r for r in sim.power_records if r.duration > 0]
        self.assertEqual(power.consumption, 2)

    def test_analysis(self):
        water, oxygen, hydrogen = self.storage(water=45)
        b = self.builder
        marker = b.element("Marker")
        b.mission(
            [
                b.create([self.plant(), water, oxygen, hydrogen], b.lsp),
                b.create([b.element("Marker 4")], b.lsp, days=4),
                b.create([marker], b.lsp, days=10),
            ]
        )
        sim = simulate(b)
        (history,) = ISRUAnalysis.create(sim).processes
        # 4 days at the full rate, then 9 kg of water for 6 days (1/6 rate)
        self.assertEqual(history.rate[0], 1)
        self.assertAlmostEqual(history.rate[1], 1 / 6)
        self.assertEqual(history.limit, [None, "Input"])
        self.assertEqual([round(m, 6) for m in history.outputs["Oxidizer"]], [32, 40])
        self.assertAlmostEqual(history.total_inputs["Water"], 45)
        self.assertAlmostEqual(history.total_outputs["Fuel"], 5)
        self.assertAlmostEqual(history.operating_days, 5)
        self.assertAlmostEqual(history.total_energy, 240)
        # 240 kWh for 40 kg of oxygen (the first output)
        self.assertAlmostEqual(history.specific_energy, 6)
        self.assertEqual(history.limits, {"Input": 6})
        analysis = SimulationAnalysis.create(b.build(), sim)
        self.assertAlmostEqual(analysis.totals.isru_output_mass, 45)
        self.assertAlmostEqual(analysis.totals.isru_energy, 240)
        self.assertEqual(len(analysis.isru.processes), 1)

    def test_input_limited(self):
        water, oxygen, hydrogen = self.storage(water=45)
        sim = self.operate([self.plant(), water, oxygen, hydrogen])
        (record,) = sim.isru_records
        self.assertAlmostEqual(record.rate, 0.5)
        self.assertEqual(record.limit, "Input")
        self.assertEqual(self.amounts(sim, oxygen), {"Oxidizer": 40})
        self.assertEqual(self.amounts(sim, water), {"Water": 0})

    def test_power_limited(self):
        # 3 kW generation less 2 kW of other consumption leaves 1 kW
        water, oxygen, hydrogen = self.storage()
        sim = self.operate(
            [self.plant(generation=3, consumption=2), water, oxygen, hydrogen]
        )
        (record,) = sim.isru_records
        self.assertAlmostEqual(record.rate, 0.5)
        self.assertEqual(record.limit, "Power")
        self.assertAlmostEqual(record.power, 1)
        (power,) = [r for r in sim.power_records if r.duration > 0]
        self.assertAlmostEqual(power.consumption, 3)
        self.assertEqual(power.deficit, 0)

    def test_storage_limited(self):
        water, oxygen, hydrogen = self.storage(oxygen_capacity=20)
        sim = self.operate([self.plant(), water, oxygen, hydrogen])
        (record,) = sim.isru_records
        self.assertAlmostEqual(record.rate, 0.25)
        self.assertEqual(record.limit, "Output Storage")
        self.assertEqual(self.amounts(sim, oxygen), {"Oxidizer": 20})

    def test_no_power_warns_once(self):
        water, oxygen, hydrogen = self.storage()
        b = self.builder
        marker = b.element("Marker")
        b.mission(
            [
                b.create(
                    [self.plant(generation=0, consumption=1), water, oxygen, hydrogen],
                    b.lsp,
                ),
                b.create([b.element("Marker 5")], b.lsp, days=5),
                b.create([marker], b.lsp, days=10),
            ]
        )
        sim = simulate(b)
        self.assertTrue(all(r.rate == 0 for r in sim.isru_records))
        self.assertEqual(len(sim.isru_records), 2)
        messages = [str(w) for w in sim.warnings if "ISRU" in str(w)]
        self.assertEqual(len(messages), 1)
        self.assertIn("no surplus power", messages[0])

    def test_unlimited_without_power(self):
        # a process without power is not constrained by power
        process = s.ISRUProcessDemandModel(
            name="Passive",
            outputs=[s.ResourceAmountRate(resource=self.builder.water.id, rate=1)],
        )
        self.builder.demand_models.append(process)
        water, _, _ = self.storage(water=0)
        sim = self.operate([self.plant(generation=0, process=process), water])
        self.assertEqual(self.amounts(sim, water), {"Water": 10})

    def test_produces_into_vehicle_tanks(self):
        b = self.builder
        lander = b.vehicle("Lander", fuel=0, max_fuel=100)
        water, oxygen, _ = self.storage()
        sim = self.operate([self.plant(), water, oxygen, lander])
        tank = sim.state.get_element(lander.id).fuel_tank
        self.assertAlmostEqual(tank.amount, 10)
        flows = [
            f for f in sim.propellant_flows if f.kind == PropellantFlowKind.CONSUMED
        ]
        self.assertEqual([round(f.amount, 6) for f in flows], [-10])
        (budget,) = PropellantAnalysis.create(sim).budgets
        self.assertAlmostEqual(budget.residual, 10)
        self.assertAlmostEqual(budget.consumed, -10)

    def test_inactive_state_does_not_operate(self):
        b = self.builder
        plant = self.plant()
        template = b.templates[-1]
        template.states.insert(0, s.State(name="Stowed", type="Dormant"))
        water, oxygen, hydrogen = self.storage()
        sim = self.operate([plant, water, oxygen, hydrogen])
        self.assertEqual(sim.isru_records, [])
        self.assertEqual(self.amounts(sim, water), {"Water": 100})

    def test_schema(self):
        with self.assertRaises(ValidationError):
            s.ISRUProcessDemandModel(name="Empty", outputs=[])
        with self.assertRaises(ValidationError):
            s.ISRUProcessDemandModel(
                name="Negative",
                outputs=[s.ResourceAmountRate(resource=self.builder.water.id, rate=1)],
                power=-1,
            )
        scenario = self.builder.build()
        data = scenario.model_dump(mode="json", by_alias=True, exclude_none=True)
        model = s.Scenario.model_validate(data).demand_models[0]
        self.assertIsInstance(model, s.ISRUProcessDemandModel)
        self.assertEqual(model.power, 2)


if __name__ == "__main__":
    unittest.main()
