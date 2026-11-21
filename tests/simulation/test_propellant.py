"""
Tests of propellant logistics: bipropellant burns, transfers between
(integral) tanks, and boiloff.
"""

import json
import math
import unittest

from spacenet import schemas as s
from spacenet.simulation import (
    EventEvaluation,
    FullSimulator,
    PreSimulator,
    PropellantAnalysis,
    SimulationAnalysis,
    TankerSizingRequest,
    size_tankers,
)
from spacenet.simulation.analysis import export_propellant
from spacenet.simulation.analysis.propellant import closed_form_flights
from spacenet.simulation.events import (
    get_achieved_delta_v,
    get_propellant_shortfall,
    get_required_fuel_mass,
)
from spacenet.simulation.records import PropellantFlowKind

from .test_analysis import SCENARIOS
from .util import ScenarioBuilder, load_scenario


def simulate(builder, cls=FullSimulator, **kwargs):
    """Simulates the scenario of a builder."""
    simulator = cls(builder.build(), **kwargs)
    simulator.simulate()
    return simulator


def amounts(sim, vehicle):
    """Gets the (fuel, oxidizer) amounts of the OMS of a vehicle."""
    element = sim.state.get_element(vehicle.id)
    system = element.get_propulsion_system(s.PropulsionType.OMS)
    return (
        system.fuel_tank.get_amount(system.fuel_tank.resource),
        system.oxidizer_tank.get_amount(system.oxidizer_tank.resource),
    )


class TestBipropellantBurns(unittest.TestCase):
    def setUp(self):
        self.builder = ScenarioBuilder()

    def test_burn_splits_by_mixture_ratio(self):
        b = self.builder
        lander = b.biprop_vehicle(mass=1000, fuel=2000, oxidizer=6000, mixture_ratio=3)
        b.mission([b.create([lander], b.leo), b.burn_event([lander], days=1)])
        sim = simulate(b)
        self.assertEqual(sim.errors, [])
        required = get_required_fuel_mass(9000, 1000, 350)
        fuel, oxidizer = amounts(sim, lander)
        self.assertAlmostEqual(fuel, 2000 - required / 4, places=6)
        self.assertAlmostEqual(oxidizer, 6000 - required * 3 / 4, places=6)

    def test_burn_is_limited_by_oxidizer(self):
        b = self.builder
        burn = s.Burn(time=0, delta_v=5000)
        b.ksc_leo.burns.append(burn)
        lander = b.biprop_vehicle(mass=1000, fuel=2000, oxidizer=3000, mixture_ratio=3)
        b.mission([b.create([lander], b.leo), b.burn_event([lander], burn, days=1)])
        sim = simulate(b)
        # 3000 kg oxidizer burns with 1000 kg fuel (4000 kg in total)
        fuel, oxidizer = amounts(sim, lander)
        self.assertEqual(oxidizer, 0)
        self.assertAlmostEqual(fuel, 1000, places=6)
        achieved = get_achieved_delta_v(6000, 350, 4000)
        self.assertIn(
            f"remaining delta-v: {5000 - achieved:.1f} m/s",
            str(sim.spatial_errors[0]),
        )
        step = sim.spatial_errors[0].event.steps[0]
        self.assertAlmostEqual(step.oxidizer_used, 3000, places=6)
        self.assertAlmostEqual(step.fuel_used, 1000, places=6)
        self.assertAlmostEqual(step.propellant_mass_used, 4000, places=6)
        self.assertAlmostEqual(
            step.propellant_shortfall,
            get_propellant_shortfall(6000, 4000, 5000, 350),
            places=6,
        )

    def test_shared_oxidizer_tank(self):
        b = self.builder
        rcs = s.PropulsionSystem(
            type="RCS",
            isp=300,
            mixture_ratio=1.5,
            shared_fuel_tank="OMS",
            shared_oxidizer_tank="OMS",
        )
        lander = b.biprop_vehicle(extra_systems=[rcs])
        b.ksc_leo.burns.append(b.rcs_burn)
        b.mission(
            [b.create([lander], b.leo), b.burn_event([lander], b.rcs_burn, days=1)]
        )
        sim = simulate(b)
        self.assertEqual(sim.errors, [])
        required = get_required_fuel_mass(9000, 10, 300)
        fuel, oxidizer = amounts(sim, lander)
        self.assertAlmostEqual(fuel, 2000 - required / 2.5, places=6)
        self.assertAlmostEqual(oxidizer, 6000 - required * 1.5 / 2.5, places=6)

    def test_shortfall_closes_the_burn(self):
        b = self.builder
        stage = b.vehicle(mass=1000, fuel=300, isp=300)
        b.mission([b.create([stage], b.leo), b.burn_event([stage], days=1)])
        sim = simulate(b)
        shortfall = sim.spatial_errors[0].event.steps[0].propellant_shortfall
        self.assertGreater(shortfall, 0)
        # fuel amounts are compared at the demand precision (0.01 units)
        b = ScenarioBuilder()
        stage = b.vehicle(mass=1000, fuel=300 + shortfall + 0.01, isp=300)
        b.mission([b.create([stage], b.leo), b.burn_event([stage], days=1)])
        sim = simulate(b)
        self.assertEqual(sim.errors, [])
        self.assertAlmostEqual(
            sim.state.get_element(stage.id).fuel_tank.get_amount(
                sim.state.get_resource(b.fuel.id)
            ),
            0,
            delta=0.02,
        )

    def test_shortfall_function(self):
        self.assertEqual(get_propellant_shortfall(1000, 900, 0, 300), 0)
        self.assertEqual(get_propellant_shortfall(1000, 900, 100, 0), math.inf)
        # enough propellant
        self.assertEqual(get_propellant_shortfall(10000, 9000, 1000, 300), 0)


class TestTankTransfers(unittest.TestCase):
    def setUp(self):
        self.builder = ScenarioBuilder()

    def _fuel(self, sim, element, selector="OMS Fuel"):
        tank = sim.state.get_element(element.id).get_tank(s.TankSelector(selector))
        return tank.get_amount(tank.resource)

    def test_transfer_to_named_rcs_tank(self):
        b = self.builder
        stage = b.vehicle(fuel=100, max_fuel=200, rcs_isp=300, rcs_fuel=0)
        stage_template = b.templates[-1]
        stage_template.propulsion_systems[1].fuel_tank.max_amount = 50
        depot = b.container(
            "Depot", contents=[s.ResourceAmount(resource=b.fuel.id, amount=80)]
        )
        b.mission(
            [
                b.create([stage, depot], b.leo),
                b.transfer(
                    depot,
                    stage,
                    b.leo,
                    days=1,
                    destination_tank="RCS Fuel",
                    resources=[s.ResourceAmount(resource=b.fuel.id, amount=30)],
                ),
            ]
        )
        sim = simulate(b)
        self.assertEqual(sim.errors, [])
        self.assertAlmostEqual(self._fuel(sim, stage, "RCS Fuel"), 30)
        self.assertAlmostEqual(self._fuel(sim, stage, "OMS Fuel"), 100)

    def test_transfer_to_missing_tank_fails(self):
        b = self.builder
        stage = b.vehicle(fuel=100, max_fuel=200)
        depot = b.container(
            "Depot", contents=[s.ResourceAmount(resource=b.fuel.id, amount=80)]
        )
        b.mission(
            [
                b.create([stage, depot], b.leo),
                b.transfer(
                    depot,
                    stage,
                    b.leo,
                    destination_tank="RCS Fuel",
                    resources=[s.ResourceAmount(resource=b.fuel.id, amount=30)],
                ),
            ]
        )
        sim = simulate(b)
        self.assertIn("has no RCS Fuel tank", str(sim.spatial_errors[0]))

    def test_transfer_routes_by_resource(self):
        b = self.builder
        lander = b.biprop_vehicle(fuel=0, oxidizer=0, max_fuel=100, max_oxidizer=300)
        depot = b.container(
            "Depot",
            max_cargo_mass=1000,
            contents=[
                s.ResourceAmount(resource=b.fuel.id, amount=100),
                s.ResourceAmount(resource=b.oxidizer.id, amount=300),
            ],
        )
        b.mission(
            [
                b.create([lander, depot], b.leo),
                b.transfer(
                    depot,
                    lander,
                    b.leo,
                    resources=[
                        s.ResourceAmount(resource=b.oxidizer.id, amount=300),
                        s.ResourceAmount(resource=b.fuel.id, amount=100),
                    ],
                ),
            ]
        )
        sim = simulate(b)
        self.assertEqual(sim.errors, [])
        self.assertEqual(amounts(sim, lander), (100, 300))

    def test_fill_destination(self):
        b = self.builder
        depot = b.biprop_vehicle("Depot", fuel=1000, oxidizer=3000)
        lander = b.biprop_vehicle(fuel=50, oxidizer=100, max_fuel=200, max_oxidizer=600)
        b.mission(
            [
                b.create([depot, lander], b.leo),
                b.transfer(
                    depot, lander, b.leo, days=1, transfer_mode="Fill Destination"
                ),
            ]
        )
        sim = simulate(b)
        self.assertEqual(sim.errors, [])
        self.assertEqual(sim.warnings, [])
        self.assertEqual(amounts(sim, lander), (200, 600))
        self.assertEqual(amounts(sim, depot), (850, 2500))
        transfer = next(
            e for e in sim.state.missions[0].events if hasattr(e, "results")
        )
        self.assertEqual(
            [(r.resource_name, r.delivered) for r in transfer.results],
            [("Fuel", 150), ("Oxidizer", 500)],
        )

    def test_fill_destination_with_losses(self):
        b = self.builder
        depot = b.biprop_vehicle("Depot", fuel=1000, oxidizer=3000)
        lander = b.biprop_vehicle(fuel=0, oxidizer=0, max_fuel=180, max_oxidizer=540)
        b.mission(
            [
                b.create([depot, lander], b.leo),
                b.transfer(
                    depot,
                    lander,
                    b.leo,
                    days=1,
                    transfer_mode="Fill Destination",
                    loss_fraction=0.1,
                ),
            ]
        )
        sim = simulate(b)
        self.assertEqual(sim.errors, [])
        fuel, oxidizer = amounts(sim, lander)
        self.assertAlmostEqual(fuel, 180, places=6)
        self.assertAlmostEqual(oxidizer, 540, places=6)
        fuel, oxidizer = amounts(sim, depot)
        self.assertAlmostEqual(fuel, 800, places=6)
        self.assertAlmostEqual(oxidizer, 2400, places=6)
        losses = [
            f.amount
            for f in sim.propellant_flows
            if f.kind == PropellantFlowKind.TRANSFER_LOSS
        ]
        self.assertEqual(len(losses), 2)
        self.assertAlmostEqual(sum(losses), 20 + 60, places=6)

    def test_fill_destination_with_insufficient_supply_warns(self):
        b = self.builder
        depot = b.biprop_vehicle("Depot", fuel=10, oxidizer=3000)
        lander = b.biprop_vehicle(fuel=0, oxidizer=0, max_fuel=100, max_oxidizer=300)
        b.mission(
            [
                b.create([depot, lander], b.leo),
                b.transfer(depot, lander, b.leo, transfer_mode="Fill Destination"),
            ]
        )
        sim = simulate(b)
        self.assertEqual(sim.errors, [])
        self.assertEqual(amounts(sim, lander), (10, 300))
        self.assertTrue(any("could not be filled" in str(w) for w in sim.warnings))

    def test_empty_origin(self):
        b = self.builder
        tanker = b.biprop_vehicle("Tanker", fuel=100, oxidizer=300)
        depot = b.biprop_vehicle(
            "Depot", fuel=0, oxidizer=0, max_fuel=1000, max_oxidizer=3000
        )
        b.mission(
            [
                b.create([tanker, depot], b.leo),
                b.transfer(tanker, depot, b.leo, transfer_mode="Empty Origin"),
            ]
        )
        sim = simulate(b)
        self.assertEqual(sim.errors, [])
        self.assertEqual(sim.warnings, [])
        self.assertEqual(amounts(sim, tanker), (0, 0))
        self.assertEqual(amounts(sim, depot), (100, 300))

    def test_empty_origin_into_selected_tank(self):
        b = self.builder
        tanker = b.biprop_vehicle("Tanker", fuel=100, oxidizer=300)
        depot = b.biprop_vehicle(
            "Depot", fuel=0, oxidizer=0, max_fuel=1000, max_oxidizer=3000
        )
        b.mission(
            [
                b.create([tanker, depot], b.leo),
                b.transfer(
                    tanker,
                    depot,
                    b.leo,
                    origin_tank="OMS Oxidizer",
                    destination_tank="OMS Oxidizer",
                    transfer_mode="Empty Origin",
                ),
            ]
        )
        sim = simulate(b)
        self.assertEqual(sim.errors, [])
        self.assertEqual(amounts(sim, tanker), (100, 0))
        self.assertEqual(amounts(sim, depot), (0, 300))


class TestBoiloff(unittest.TestCase):
    def setUp(self):
        self.builder = ScenarioBuilder()

    def _scenario(self, rate=0.01, location=None, extra_days=()):
        b = self.builder
        depot = b.biprop_vehicle("Depot", fuel=1000, oxidizer=3000, boiloff_rate=rate)
        events = [b.create([depot], location or b.leo)]
        for days in (*extra_days, 10):
            marker = b.element(f"Marker {days}")
            events.append(b.create([marker], b.leo, days=days))
        b.mission(events)
        return depot

    def test_boiloff_is_a_fraction_of_capacity(self):
        depot = self._scenario()
        sim = simulate(self.builder)
        fuel, oxidizer = amounts(sim, depot)
        self.assertAlmostEqual(fuel, 900, places=6)
        self.assertAlmostEqual(oxidizer, 2700, places=6)
        self.assertEqual(sim.unsatisfied_demands, [])
        boiloff = [
            f for f in sim.propellant_flows if f.kind == PropellantFlowKind.BOILOFF
        ]
        self.assertAlmostEqual(sum(f.amount for f in boiloff), 400, places=6)
        self.assertTrue(all(f.event_name is None for f in boiloff))

    def test_boiloff_does_not_depend_on_events(self):
        depot = self._scenario(extra_days=(2.5, 5, 7))
        sim = simulate(self.builder)
        fuel, oxidizer = amounts(sim, depot)
        self.assertAlmostEqual(fuel, 900, places=6)
        self.assertAlmostEqual(oxidizer, 2700, places=6)

    def test_boiloff_stops_when_empty(self):
        depot = self._scenario(rate=0.2)
        sim = simulate(self.builder)
        self.assertEqual(amounts(sim, depot), (0, 0))

    def test_no_boiloff_on_earth_surface(self):
        depot = self._scenario(location=self.builder.ksc)
        sim = simulate(self.builder)
        self.assertEqual(amounts(sim, depot), (1000, 3000))

    def test_pre_simulator_includes_boiloff(self):
        depot = self._scenario()
        sim = PreSimulator(self.builder.build())
        sim.simulate(5)
        fuel, _ = amounts(sim, depot)
        self.assertAlmostEqual(fuel, 950, places=6)

    def test_flows_are_recorded(self):
        depot = self._scenario()
        sim = simulate(self.builder)
        loaded = [
            f
            for f in sim.propellant_flows
            if f.kind == PropellantFlowKind.LOADED and f.vehicle_id == depot.id
        ]
        self.assertEqual(
            sorted((f.tank_key, f.amount) for f in loaded),
            [("OMS Fuel", 1000), ("OMS Oxidizer", 3000)],
        )


def build_refueling():
    """
    Builds a scenario in which a tanker offloads into a depot, the depot
    boils off, refuels a lander with losses, and the lander burns.
    """
    b = ScenarioBuilder()
    depot = b.biprop_vehicle(
        "Depot",
        fuel=0,
        oxidizer=0,
        max_fuel=2000,
        max_oxidizer=6000,
        boiloff_rate=0.001,
    )
    tanker = b.biprop_vehicle("Tanker", fuel=1000, oxidizer=3000)
    lander = b.biprop_vehicle(
        fuel=0, oxidizer=0, max_fuel=500, max_oxidizer=1500, boiloff_rate=0.002
    )
    b.mission(
        [
            b.create([depot, tanker, lander], b.leo),
            b.transfer(tanker, depot, b.leo, days=1, transfer_mode="Empty Origin"),
            b.transfer(
                depot,
                lander,
                b.leo,
                days=10,
                transfer_mode="Fill Destination",
                loss_fraction=0.05,
            ),
            b.burn_event([lander], days=12),
        ]
    )
    return b, depot, tanker, lander


class TestPropellantAnalysis(unittest.TestCase):
    def _check_budgets(self, analysis, sim=None):
        for budget in analysis.budgets:
            balance = (
                budget.loaded
                + budget.added
                + budget.transferred_in
                - budget.transferred_out
                - budget.transfer_loss
                - budget.burned
                - budget.boiloff
                - budget.consumed
            )
            self.assertAlmostEqual(balance, budget.residual, places=6, msg=budget.tank)
        for history, budget in zip(analysis.tanks, analysis.budgets):
            self.assertEqual(history.points[-1][1], budget.residual)
            if sim is not None and history.vehicle_id in sim.state.network.registrar:
                vehicle = sim.state.get_element(history.vehicle_id)
                tank = vehicle.get_tank(s.TankSelector(history.tank))
                self.assertAlmostEqual(
                    tank.get_amount(tank.resource), budget.residual, places=6
                )

    def test_budgets_close_on_fixtures(self):
        for path in SCENARIOS:
            with self.subTest(path=path):
                sim = FullSimulator(load_scenario(path))
                sim.simulate()
                analysis = PropellantAnalysis.create(sim)
                self._check_budgets(analysis)
                self.assertTrue(
                    all(
                        t.points == sorted(t.points, key=lambda p: p[0])
                        for t in analysis.tanks
                    )
                )

    def test_refueling_budget(self):
        b, depot, tanker, lander = build_refueling()
        sim = FullSimulator(b.build())
        sim.simulate()
        self.assertEqual(sim.errors, [])
        analysis = PropellantAnalysis.create(sim)
        self._check_budgets(analysis, sim)
        budgets = {(x.vehicle_name, x.tank): x for x in analysis.budgets}
        depot_fuel = budgets[("Depot", "OMS Fuel")]
        self.assertEqual(depot_fuel.transferred_in, 1000)
        # 2 kg/day of boiloff for 9 days before refueling the lander
        self.assertAlmostEqual(depot_fuel.boiloff, 18 + 2 * 2, places=6)
        self.assertAlmostEqual(depot_fuel.transferred_out, 500, places=6)
        self.assertAlmostEqual(depot_fuel.transfer_loss, 500 / 0.95 - 500, places=6)
        lander_fuel = budgets[("Lander", "OMS Fuel")]
        self.assertEqual(len(lander_fuel.burns), 1)
        self.assertGreater(lander_fuel.burned, 0)
        self.assertEqual(budgets[("Tanker", "OMS Oxidizer")].residual, 0)
        history = next(
            t
            for t in analysis.tanks
            if (t.vehicle_name, t.tank) == ("Depot", "OMS Fuel")
        )
        self.assertEqual(history.points[0], (0, 0))
        self.assertIn((1, 1000), history.points)
        self.assertEqual(history.points[-1][0], 12)

    def test_simulation_analysis_reports_propellant(self):
        b, *_ = build_refueling()
        analysis = SimulationAnalysis.create(b.build())
        totals = analysis.totals
        self.assertAlmostEqual(
            totals.propellant_boiloff_mass, analysis.propellant.totals.boiloff_mass
        )
        self.assertGreater(totals.propellant_boiloff_mass, 0)
        self.assertGreater(totals.propellant_transfer_loss_mass, 0)
        self.assertGreater(totals.propellant_burned_mass, 0)
        data = json.loads(analysis.model_dump_json(by_alias=True))
        self.assertIn("budgets", data["propellant"])
        self.assertIn("propellantBoiloffMass", data["totals"])

    def test_export_propellant(self):
        b, *_ = build_refueling()
        sim = FullSimulator(b.build())
        sim.simulate()
        text = export_propellant(PropellantAnalysis.create(sim))
        lines = text.splitlines()
        self.assertTrue(lines[0].startswith("Vehicle,Tank,Resource"))
        self.assertEqual(len(lines), 1 + 6)

    def test_evaluate_transfer(self):
        b, depot, _, lander = build_refueling()
        scenario = b.build()
        draft = scenario.mission_list[0].events[2]
        evaluation = EventEvaluation.create(scenario, 0, draft, 2)
        self.assertEqual(evaluation.issues, [])
        self.assertEqual(
            [(t.resource_name, round(t.delivered, 6)) for t in evaluation.transfers],
            [("Fuel", 500), ("Oxidizer", 1500)],
        )
        self.assertTrue(all(t.destination_space == 0 for t in evaluation.transfers))
        self.assertEqual(evaluation.container.name, lander.name)
        tanks = {t.key: t for t in evaluation.container.fuel_tanks}
        self.assertEqual(tanks["OMS Oxidizer"].role, "Oxidizer")
        self.assertEqual(tanks["OMS Oxidizer"].label, "OMS Oxidizer")
        self.assertEqual(tanks["OMS Fuel"].boiloff_rate, 0.002)


class TestTankerSizing(unittest.TestCase):
    def test_without_boiloff(self):
        sizing = size_tankers(
            TankerSizingRequest(required=1000, tanker_delivery=150, depot_capacity=2000)
        )
        self.assertTrue(sizing.feasible)
        self.assertEqual(sizing.flights, 7)
        self.assertEqual(sizing.final, 1050)
        self.assertEqual(sizing.spilled, 0)

    def test_matches_closed_form(self):
        for boiloff_rate, interval, loiter, loss in (
            (0.001, 10, 5, 0),
            (0.002, 7, 30, 0.05),
            (0.0005, 3, 0, 0.02),
        ):
            request = TankerSizingRequest(
                required=1200,
                tanker_delivery=100,
                depot_capacity=1500,
                boiloff_rate=boiloff_rate,
                interval_days=interval,
                loiter_days=loiter,
                transfer_loss=loss,
            )
            with self.subTest(request=request):
                sizing = size_tankers(request)
                self.assertTrue(sizing.feasible)
                self.assertEqual(
                    sizing.flights, math.ceil(closed_form_flights(request))
                )
                self.assertGreaterEqual(sizing.final, 1200)
                self.assertAlmostEqual(
                    sizing.delivered - sizing.boiloff, sizing.final, places=6
                )

    def test_initial_propellant_suffices(self):
        sizing = size_tankers(
            TankerSizingRequest(required=100, tanker_delivery=50, initial=100)
        )
        self.assertEqual(sizing.flights, 0)

    def test_capacity_spills_offloads(self):
        sizing = size_tankers(
            TankerSizingRequest(required=1000, tanker_delivery=400, depot_capacity=1000)
        )
        self.assertEqual(sizing.flights, 3)
        self.assertEqual(sizing.spilled, 200)

    def test_infeasible(self):
        sizing = size_tankers(
            TankerSizingRequest(
                required=1000,
                tanker_delivery=100,
                boiloff_rate=0.01,
                interval_days=10,
            )
        )
        self.assertFalse(sizing.feasible)
        self.assertIsNone(sizing.flights)
        self.assertIn("boils off", sizing.reason)
        sizing = size_tankers(
            TankerSizingRequest(required=1000, tanker_delivery=100, depot_capacity=500)
        )
        self.assertIn("capacity", sizing.reason)
        sizing = size_tankers(
            TankerSizingRequest(required=1000, tanker_delivery=10, max_flights=20)
        )
        self.assertIn("More than 20", sizing.reason)
