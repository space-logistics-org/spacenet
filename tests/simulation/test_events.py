"""
Tests of simulation events.
"""

import math
import unittest
from datetime import timedelta

from spacenet import schemas as s
from spacenet.simulation import FullSimulator, MiniSimulator
from spacenet.simulation.events import G0, get_achieved_delta_v, get_required_fuel_mass

from .util import ScenarioBuilder


def simulate(builder, cls=FullSimulator, **kwargs):
    """Simulates the scenario of a builder."""
    simulator = cls(builder.build(), **kwargs)
    simulator.simulate()
    return simulator


def event(cls, builder, location, days=0, priority=1, **kwargs):
    """Makes an event at a location."""
    return cls(
        name=cls.__name__,
        priority=priority,
        mission_time=timedelta(days=days),
        location=location.id,
        **kwargs,
    )


class TestElementEvents(unittest.TestCase):
    def setUp(self):
        self.builder = ScenarioBuilder()
        self.lander = self.builder.carrier("Lander")
        self.crew = self.builder.crew()
        self.cargo = self.builder.element("Cargo", mass=500, class_of_supply=601)

    def test_create_and_move(self):
        b = self.builder
        b.mission(
            [
                b.create([self.lander, self.cargo], b.ksc),
                b.create([self.crew], self.lander, location=b.ksc, priority=2),
                b.move([self.cargo], self.lander, b.ksc, days=1),
            ]
        )
        sim = simulate(b)
        self.assertEqual(sim.errors, [])
        self.assertEqual(sim.warnings, [])
        lander = sim.state.get_element(self.lander.id)
        self.assertEqual(lander.location.name, "KSC")
        self.assertEqual([e.name for e in lander.contents], ["Cargo", "Crew"])
        self.assertEqual(lander.total_mass, 1600)
        self.assertEqual(len(sim.state.network.registrar), 3)

    def test_create_existing_element_fails(self):
        b = self.builder
        b.mission(
            [b.create([self.cargo], b.ksc), b.create([self.cargo], b.ksc, days=1)]
        )
        sim = simulate(b)
        self.assertEqual(len(sim.spatial_errors), 1)
        self.assertIn("already exists at KSC", str(sim.spatial_errors[0]))
        self.assertEqual(sim.spatial_errors[0].time, 1)

    def test_create_in_missing_carrier_fails(self):
        b = self.builder
        b.mission([b.create([self.cargo], self.lander, location=b.ksc)])
        sim = simulate(b)
        self.assertIn("Lander was not found", str(sim.spatial_errors[0]))

    def test_move_from_wrong_location_fails(self):
        b = self.builder
        b.mission(
            [b.create([self.cargo], b.ksc), b.move([self.cargo], b.lsp, b.leo, days=1)]
        )
        sim = simulate(b)
        self.assertIn("is located at KSC instead of LEO", str(sim.spatial_errors[0]))
        self.assertEqual(sim.state.get_element(self.cargo.id).location.name, "KSC")

    def test_move_over_capacity_fails(self):
        b = self.builder
        heavy = b.element("Heavy", mass=6000)
        b.mission(
            [b.create([self.lander, heavy], b.ksc), b.move([heavy], self.lander, b.ksc)]
        )
        sim = simulate(b)
        self.assertIn("could not be added to Lander", str(sim.spatial_errors[0]))

    def test_events_without_elements_warn(self):
        b = self.builder
        b.mission([b.create([], b.ksc), b.move([], b.ksc, b.ksc)])
        sim = simulate(b)
        self.assertEqual(sim.errors, [])
        self.assertEqual(
            [w.message for w in sim.warnings], ["No elements defined."] * 2
        )

    def test_remove(self):
        b = self.builder
        b.mission(
            [
                b.create([self.lander], b.ksc),
                b.create([self.crew], self.lander, location=b.ksc, priority=2),
                event(s.RemoveElements, b, b.ksc, days=1, elements=[self.lander.id]),
            ]
        )
        sim = simulate(b)
        self.assertEqual(sim.errors, [])
        self.assertEqual(len(sim.state.network.registrar), 0)
        self.assertEqual(len(sim.state.network.removed_registrar), 2)
        self.assertIsNone(sim.state.get_element(self.lander.id).location)

    def test_reconfigure(self):
        b = self.builder
        rover = b.add(
            s.Element(
                name="Station",
                states=[
                    s.State(name="On", type="Active"),
                    s.State(name="Off", type="Quiescent"),
                ],
                current_state_index=0,
            ),
            s.InstElement,
        )
        b.mission(
            [
                b.create([rover, self.cargo], b.ksc),
                event(
                    s.ReconfigureElement,
                    b,
                    b.ksc,
                    days=1,
                    element=rover.id,
                    state_index=1,
                ),
                event(
                    s.ReconfigureElements,
                    b,
                    b.ksc,
                    days=2,
                    elements=[rover.id, self.cargo.id],
                    state_type="Active",
                ),
                event(
                    s.ReconfigureElement,
                    b,
                    b.ksc,
                    days=3,
                    element=rover.id,
                    state_index=-1,
                ),
            ]
        )
        sim = simulate(b, MiniSimulator)
        self.assertEqual(sim.state.get_element(rover.id).current_state.name, "On")
        # the stateless element has no active state
        self.assertEqual(
            [w.message for w in sim.warnings], ["No Active state for Cargo."]
        )
        # an element with states cannot be reconfigured to no state
        self.assertIn("does not contain state None", str(sim.spatial_errors[0]))


class TestResourceEvents(unittest.TestCase):
    def setUp(self):
        self.builder = b = ScenarioBuilder()
        self.tank = b.container(
            "Tank A", contents=[s.ResourceAmount(resource=b.water.id, amount=50)]
        )
        self.other = b.container("Tank B")
        self.water = [s.ResourceAmount(resource=b.water.id, amount=30)]

    def test_add_transfer_and_consume(self):
        b = self.builder
        b.mission(
            [
                b.create([self.tank, self.other], b.ksc),
                event(
                    s.AddResources,
                    b,
                    b.ksc,
                    days=1,
                    container=self.tank.id,
                    resources=self.water,
                ),
                event(
                    s.TransferResources,
                    b,
                    b.ksc,
                    days=2,
                    origin_container=self.tank.id,
                    destination_container=self.other.id,
                    resources=self.water,
                ),
                event(
                    s.ConsumeResources,
                    b,
                    b.ksc,
                    days=3,
                    source=self.other.id,
                    resources=[s.ResourceAmount(resource=b.water.id, amount=90)],
                ),
            ]
        )
        sim = simulate(b)
        self.assertEqual(sim.spatial_errors, [])
        water = sim.state.get_resource(b.water.id)
        self.assertEqual(sim.state.get_element(self.tank.id).get_amount(water), 0)
        self.assertEqual(sim.state.get_element(self.other.id).get_amount(water), 0)
        # 80 units were available at the location to satisfy the demand for 90
        self.assertEqual(len(sim.unsatisfied_demands), 1)
        demand = sim.unsatisfied_demands[0]
        self.assertEqual(demand.time, 3)
        self.assertEqual(demand.element.name, "Tank B")
        self.assertEqual(demand.demands.get(water).amount, 10)

    def test_demands_not_satisfied(self):
        b = self.builder
        b.mission(
            [
                b.create([self.tank], b.ksc),
                event(
                    s.ConsumeResources,
                    b,
                    b.ksc,
                    days=1,
                    source=self.tank.id,
                    resources=self.water,
                ),
            ]
        )
        sim = simulate(b, demands_satisfied=False, packing_demands_added=True)
        water = sim.state.get_resource(b.water.id)
        self.assertEqual(sim.state.get_element(self.tank.id).get_amount(water), 50)
        demands = sim.unsatisfied_demands[0].demands
        self.assertEqual(demands.get(water).amount, 30)
        # packing demands are added using the resource packing factor
        self.assertEqual(demands.get(sim.state.get_resource(5)).amount, 15)

    def test_add_over_capacity_fails(self):
        b = self.builder
        b.mission(
            [
                b.create([self.tank], b.ksc),
                event(
                    s.AddResources,
                    b,
                    b.ksc,
                    container=self.tank.id,
                    resources=[s.ResourceAmount(resource=b.water.id, amount=51)],
                    priority=2,
                ),
            ]
        )
        sim = simulate(b)
        self.assertIn("could not be added to Tank A", str(sim.spatial_errors[0]))

    def test_transfer_more_than_available_fails(self):
        b = self.builder
        b.mission(
            [
                b.create([self.tank, self.other], b.ksc),
                event(
                    s.TransferResources,
                    b,
                    b.ksc,
                    days=1,
                    origin_container=self.other.id,
                    destination_container=self.tank.id,
                    resources=self.water,
                ),
            ]
        )
        sim = simulate(b)
        self.assertIn("could not be removed from Tank B", str(sim.spatial_errors[0]))

    def test_vehicle_fuel_tank_is_a_resource_container(self):
        b = self.builder
        stage = b.vehicle(fuel=100, max_fuel=200)
        b.mission(
            [
                b.create([stage], b.ksc),
                event(
                    s.AddResources,
                    b,
                    b.ksc,
                    days=1,
                    container=stage.id,
                    resources=[s.ResourceAmount(resource=b.fuel.id, amount=50)],
                ),
            ]
        )
        sim = simulate(b)
        self.assertEqual(sim.errors, [])
        self.assertEqual(sim.state.get_element(stage.id).fuel_tank.amount, 150)

    def test_element_is_not_a_resource_container(self):
        b = self.builder
        cargo = b.element("Cargo")
        b.mission(
            [
                b.create([cargo], b.ksc),
                event(
                    s.AddResources,
                    b,
                    b.ksc,
                    days=1,
                    container=cargo.id,
                    resources=self.water,
                ),
            ]
        )
        sim = simulate(b)
        self.assertIn("Cargo is not a resource container", str(sim.spatial_errors[0]))


class TestTransportEvents(unittest.TestCase):
    def setUp(self):
        self.builder = ScenarioBuilder()

    def test_rocket_equation(self):
        fuel = get_required_fuel_mass(10000, 1000, 300)
        self.assertAlmostEqual(fuel, 10000 * (1 - math.exp(-1000 / (300 * G0))))
        self.assertAlmostEqual(get_achieved_delta_v(10000, 300, fuel), 1000)
        self.assertEqual(get_achieved_delta_v(10000, 300, 0), 0)

    def _space_transport(self, elements, actions, **kwargs):
        b = self.builder
        return event(
            s.SpaceTransport,
            b,
            b.ksc,
            priority=2,
            edge=b.ksc_leo.id,
            elements=[e.id for e in elements],
            burn_stage_sequence=[
                s.BurnStageSequence(
                    burn=b.burn.id,
                    actions=[s.BurnStageItem(type=t, element=e.id) for t, e in actions],
                )
            ],
            **kwargs,
        )

    def test_space_transport_burn(self):
        b = self.builder
        stage = b.vehicle(mass=1000, fuel=9000, isp=300)
        b.mission(
            [
                b.create([stage], b.ksc),
                self._space_transport([stage], [("Burn", stage)]),
            ]
        )
        sim = simulate(b)
        self.assertEqual(sim.errors, [])
        element = sim.state.get_element(stage.id)
        self.assertEqual(element.location.name, "LEO")
        self.assertEqual(sim.time, 0.25)
        self.assertAlmostEqual(
            element.fuel_tank.amount,
            9000 - get_required_fuel_mass(10000, 1000, 300),
            places=2,
        )
        # the element is on the edge during the transport
        on_edge = [n for n in sim.network_history if n.get_elements(b.ksc_leo.id)]
        self.assertEqual([n.time for n in on_edge], [0])

    def test_space_transport_staging(self):
        b = self.builder
        booster = b.vehicle("Booster", mass=1000, fuel=1000, isp=300)
        upper = b.vehicle("Upper", mass=500, fuel=3000, isp=400)
        payload = b.element("Payload", mass=500)
        b.mission(
            [
                b.create([booster, upper, payload], b.ksc),
                self._space_transport(
                    [booster, upper, payload],
                    [("Burn", booster), ("Stage", booster), ("Burn", upper)],
                ),
            ]
        )
        sim = simulate(b)
        self.assertEqual(sim.errors, [])
        first = get_achieved_delta_v(6000, 300, 1000)
        remaining_fuel = 3000 - get_required_fuel_mass(4000, 1000 - first, 400)
        self.assertAlmostEqual(
            sim.state.get_element(upper.id).fuel_tank.amount, remaining_fuel, places=2
        )
        self.assertEqual(sim.state.get_element(booster.id).fuel_tank.amount, 0)
        # the staged booster is removed and does not arrive at the destination
        self.assertIsNone(sim.state.get_element(booster.id).location)
        self.assertIn(booster.id, sim.state.network.removed_registrar)
        leo = sim.state.get_location(b.leo.id)
        self.assertEqual([e.name for e in leo.contents], ["Payload", "Upper"])

    def test_space_transport_insufficient_delta_v(self):
        b = self.builder
        stage = b.vehicle(mass=1000, fuel=100, isp=300)
        b.mission(
            [
                b.create([stage], b.ksc),
                self._space_transport([stage], [("Burn", stage)]),
            ]
        )
        sim = simulate(b)
        achieved = get_achieved_delta_v(1100, 300, 100)
        self.assertEqual(len(sim.spatial_errors), 1)
        self.assertIn(
            f"remaining delta-v: {1000 - achieved:.1f} m/s", str(sim.spatial_errors[0])
        )
        self.assertEqual(sim.state.get_element(stage.id).fuel_tank.amount, 0)

    def test_space_transport_without_burn_actions(self):
        b = self.builder
        stage = b.vehicle()
        b.mission([b.create([stage], b.ksc), self._space_transport([stage], [])])
        sim = simulate(b)
        self.assertIn("remaining delta-v: 1000.0 m/s", str(sim.spatial_errors[0]))

    def test_burn_requires_propulsive_vehicle(self):
        b = self.builder
        cargo = b.element("Cargo", mass=10)
        b.mission(
            [
                b.create([cargo], b.ksc),
                self._space_transport([cargo], [("Burn", cargo)]),
            ]
        )
        sim = simulate(b)
        self.assertIn("Cargo is not a propulsive vehicle", str(sim.spatial_errors[0]))

    def test_propulsive_burn_event(self):
        b = self.builder
        stage = b.vehicle(mass=1000, fuel=9000, isp=300)
        b.mission(
            [
                b.create([stage], b.ksc),
                event(
                    s.PropulsiveBurn,
                    b,
                    b.ksc,
                    days=1,
                    elements=[stage.id],
                    burn=b.burn.id,
                    burn_stage_sequence=[
                        s.BurnStageItem(type="Burn", element=stage.id)
                    ],
                ),
            ]
        )
        sim = simulate(b)
        self.assertEqual(sim.errors, [])
        self.assertAlmostEqual(
            sim.state.get_element(stage.id).fuel_tank.amount,
            9000 - get_required_fuel_mass(10000, 1000, 300),
            places=2,
        )

    def test_flight_transport(self):
        b = self.builder
        lander = b.carrier("Lander", mass=4000)
        crew = [b.crew("A"), b.crew("B")]
        b.mission(
            [
                b.create([lander], b.ksc),
                b.create(crew, lander, location=b.ksc, priority=2),
                b.flight([lander], b.ksc_lsp, priority=3),
            ]
        )
        sim = simulate(b)
        self.assertEqual(sim.errors, [])
        self.assertEqual(sim.time, 3)
        self.assertEqual(sim.state.get_element(lander.id).location.name, "LSP")
        self.assertEqual(sim.state.get_element(crew[0].id).location.name, "LSP")

    def test_flight_transport_over_mass_capacity(self):
        b = self.builder
        lander = b.carrier("Lander", mass=10001)
        b.mission([b.create([lander], b.ksc), b.flight([lander], b.ksc_lsp)])
        sim = simulate(b)
        self.assertIn(
            "Flight cargo mass over capacity: 10001.0/10000.0 kg",
            str(sim.spatial_errors[0]),
        )
        self.assertEqual(sim.state.get_element(lander.id).location.name, "KSC")

    def test_flight_transport_over_crew_capacity(self):
        b = self.builder
        lander = b.carrier("Lander", max_crew=3)
        capsule = b.carrier("Capsule", mass=100, max_crew=3)
        crew = [b.crew("A"), b.crew("B"), b.crew("C")]
        b.mission(
            [
                b.create([lander], b.ksc),
                b.create([capsule], lander, location=b.ksc, priority=2),
                b.create(crew, capsule, location=b.ksc, priority=3),
                b.flight([lander], b.ksc_lsp, priority=4),
            ]
        )
        sim = simulate(b)
        # crew members inside nested carriers count towards the crew capacity
        self.assertIn("Flight crew size over capacity: 3/2", str(sim.spatial_errors[0]))

    def test_surface_transport(self):
        b = self.builder
        rover = b.add(
            s.SurfaceVehicle(
                name="Rover",
                mass=500,
                max_cargo_mass=100,
                max_crew=2,
                max_speed=10,
                max_fuel=100,
                fuel=s.ResourceAmount(resource=b.fuel.id, amount=100),
                states=[
                    s.State(name="Parked", type="Quiescent"),
                    s.State(name="Driving", type="Active"),
                ],
                current_state_index=0,
            ),
            s.InstSurfaceVehicle,
        )

        def drive(location, days):
            return event(
                s.SurfaceTransport,
                b,
                location,
                days=days,
                priority=2,
                edge=b.lsp_lsp2.id,
                vehicle=rover.id,
                transport_state=1,
                speed=2,
                duty_cycle=0.5,
            )

        b.mission([b.create([rover], b.lsp), drive(b.lsp, 0), drive(b.lsp2, 5)])
        sim = simulate(b)
        self.assertEqual(sim.errors, [])
        element = sim.state.get_element(rover.id)
        # 86.4 km at 2 m/s for half of the time takes one day in each direction
        self.assertEqual(sim.time, 6)
        self.assertEqual(element.location.name, "LSP")
        self.assertEqual(element.current_state.name, "Parked")
        states = {
            n.time: [
                (n.location_names[i], e.state)
                for i, es in n.locations.items()
                for e in es
            ]
            for n in sim.network_history
        }
        self.assertEqual(states[0], [("LSP-LSP2", "Driving")])
        self.assertEqual(states[1], [("LSP2", "Parked")])
        self.assertEqual(states[5], [("LSP-LSP2", "Driving")])
        self.assertEqual(states[6], [("LSP", "Parked")])

    def test_surface_transport_is_optional_state(self):
        b = self.builder
        rover = b.rover()
        b.mission(
            [
                b.create([rover], b.lsp),
                event(
                    s.SurfaceTransport,
                    b,
                    b.lsp,
                    priority=2,
                    edge=b.lsp_lsp2.id,
                    vehicle=rover.id,
                    speed=1,
                ),
            ]
        )
        sim = simulate(b)
        self.assertEqual(sim.errors, [])
        self.assertEqual(sim.time, 1)
        self.assertEqual(sim.state.get_element(rover.id).location.name, "LSP2")


class TestExplorationEvents(unittest.TestCase):
    def setUp(self):
        self.builder = b = ScenarioBuilder()
        self.habitat = b.carrier("Habitat")
        self.crew = [
            b.add(
                s.HumanAgent(
                    name=name,
                    mass=100,
                    active_time_fraction=0.5,
                    states=[
                        s.State(name="IVA", type="Active"),
                        s.State(name="EVA", type="Active"),
                    ],
                    current_state_index=0,
                ),
                s.InstHumanAgent,
            )
            for name in ("A", "B")
        ]
        self.setup = [
            b.create([self.habitat], b.lsp),
            b.create(self.crew, self.habitat, location=b.lsp, priority=2),
        ]
        self.states = [s.ElementState(element=c.id, state_index=1) for c in self.crew]

    def _history(self, sim):
        crew = sim.state.get_element(self.crew[0].id)
        return [
            (snapshot.time, str(snapshot.get_container(crew)))
            for snapshot in sim.location_history
            if snapshot.get_container(crew) is not None
        ]

    def test_eva(self):
        b = self.builder
        b.mission(
            self.setup
            + [
                event(
                    s.CrewedEVA,
                    b,
                    b.lsp,
                    days=1,
                    vehicle=self.habitat.id,
                    eva_duration=timedelta(hours=6),
                    element_states=self.states,
                    additional_demands=[
                        s.GenericResourceAmount(
                            class_of_supply=203, environment="Unpressurized", amount=2
                        )
                    ],
                )
            ]
        )
        sim = simulate(b, MiniSimulator)
        self.assertEqual(sim.spatial_errors, [])
        history = self._history(sim)
        # the crew is outside of the habitat between 1.0 and 1.25 days
        self.assertIn((1.0, "LSP"), history)
        self.assertEqual(history[-1], (1.25, "Habitat"))
        crew = sim.state.get_element(self.crew[0].id)
        self.assertEqual(crew.current_state.name, "IVA")
        # additional demands occur at the end of the activity
        self.assertEqual(len(sim.unsatisfied_demands), 1)
        self.assertEqual(sim.unsatisfied_demands[0].time, 1.25)
        self.assertEqual(sim.unsatisfied_demands[0].element.name, "Habitat")
        self.assertEqual(sim.unsatisfied_demands[0].demands.total_mass, 2)

    def test_eva_is_not_detailed(self):
        b = ScenarioBuilder(detailed_eva=False)
        habitat = b.carrier("Habitat")
        crew = b.crew()
        b.mission(
            [
                b.create([habitat], b.lsp),
                b.create([crew], habitat, location=b.lsp, priority=2),
                event(
                    s.CrewedEVA,
                    b,
                    b.lsp,
                    days=1,
                    vehicle=habitat.id,
                    eva_duration=timedelta(hours=6),
                    element_states=[s.ElementState(element=crew.id, state_index=-1)],
                    additional_demands=[],
                ),
            ]
        )
        sim = simulate(b)
        self.assertEqual(sim.errors, [])
        self.assertEqual(sim.time, 1)

    def test_eva_requires_vehicle_at_location(self):
        b = self.builder
        b.mission(
            self.setup
            + [
                event(
                    s.CrewedEVA,
                    b,
                    b.lsp2,
                    days=1,
                    vehicle=self.habitat.id,
                    eva_duration=timedelta(hours=6),
                    element_states=self.states,
                    additional_demands=[],
                )
            ]
        )
        sim = simulate(b)
        self.assertIn(
            "Habitat is located at LSP instead of LSP2", str(sim.spatial_errors[0])
        )

    def test_exploration(self):
        b = self.builder
        b.mission(
            self.setup
            + [
                event(
                    s.CrewedExploration,
                    b,
                    b.lsp,
                    days=1,
                    vehicle=self.habitat.id,
                    duration=timedelta(days=7),
                    eva_per_week=5,
                    eva_duration=timedelta(hours=8),
                    element_states=self.states,
                )
            ]
        )
        sim = simulate(b, MiniSimulator)
        self.assertEqual(sim.errors, [])
        mission = sim.state.missions[0]
        exploration = mission.events[-1]
        self.assertEqual(exploration.number_eva, 5)
        self.assertAlmostEqual(exploration.hours_between_eva, (7 * 24 - 5 * 8) / 6)
        self.assertEqual(mission.number_eva, 5)
        self.assertEqual(mission.eva_crew_time, 80)
        self.assertEqual(mission.duration, 8)
        egress = [t for t, container in self._history(sim) if container == "LSP"]
        # the crew is outside of the habitat at the start and end of each activity
        self.assertEqual(len(set(egress)), 10)
        # the first activity starts after one period between activities
        self.assertAlmostEqual(
            min(egress), 1 + exploration.hours_between_eva / 24, delta=0.03
        )

    def test_exploration_is_not_detailed(self):
        b = ScenarioBuilder(detailed_exploration=False)
        habitat = b.carrier("Habitat")
        crew = b.crew()
        b.mission(
            [
                b.create([habitat], b.lsp),
                b.create([crew], habitat, location=b.lsp, priority=2),
                event(
                    s.CrewedExploration,
                    b,
                    b.lsp,
                    days=1,
                    vehicle=habitat.id,
                    duration=timedelta(days=7),
                    eva_per_week=5,
                    eva_duration=timedelta(hours=8),
                    element_states=[s.ElementState(element=crew.id, state_index=-1)],
                ),
            ]
        )
        sim = simulate(b, MiniSimulator)
        self.assertEqual(sim.errors, [])
        # the crew never leaves the habitat
        member = sim.state.get_element(crew.id)
        containers = {str(n.get_container(member)) for n in sim.location_history}
        self.assertEqual(containers - {"None"}, {"Habitat"})
        self.assertEqual(sim.state.missions[0].eva_crew_time, 40)


if __name__ == "__main__":
    unittest.main()
