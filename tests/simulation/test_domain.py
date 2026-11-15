"""
Tests of simulation settings, resources, elements, and demand models.
"""

import unittest
from datetime import timedelta

from spacenet import schemas as s
from spacenet.simulation import (
    Demand,
    DemandSet,
    FullSimulator,
    Settings,
    SimCarrier,
    SimCrewMember,
    SimElement,
    SimPropulsionSystem,
    SimPropulsiveVehicle,
    SimResource,
    SimResourceContainer,
    SimResourceTank,
    State,
)
from spacenet.simulation.settings import java_round

from .util import ScenarioBuilder


class TestSettings(unittest.TestCase):
    def test_java_round_rounds_half_up(self):
        self.assertEqual(java_round(0.5), 1)
        self.assertEqual(java_round(1.5), 2)
        self.assertEqual(java_round(2.5), 3)
        self.assertEqual(java_round(-0.5), 0)
        self.assertEqual(java_round(2.4), 2)

    def test_round_time(self):
        settings = Settings()
        self.assertAlmostEqual(settings.round_time(0.26), 0.25)
        self.assertAlmostEqual(settings.round_time(0.275), 0.3)
        self.assertAlmostEqual(settings.round_time(7.5), 7.5)
        self.assertEqual(settings.round_time(float("inf")), float("inf"))

    def test_round_mass_demand_volume(self):
        settings = Settings()
        self.assertAlmostEqual(settings.round_mass(1.234), 1.23)
        self.assertAlmostEqual(settings.round_demand(1.235), 1.24)
        self.assertAlmostEqual(settings.round_volume(1.23456789), 1.234568)

    def test_zero_precision_does_not_round(self):
        settings = Settings(s.Configuration(mass_precision=0, time_precision=0))
        self.assertEqual(settings.round_mass(1.23456), 1.23456)
        self.assertEqual(settings.round_time(1.23456), 1.23456)

    def test_delegates_to_configuration(self):
        settings = Settings(s.Configuration(volume_constrained=True))
        self.assertTrue(settings.volume_constrained)
        with self.assertRaises(AttributeError):
            settings.unknown_option  # pylint: disable=pointless-statement


class TestResources(unittest.TestCase):
    def setUp(self):
        self.settings = Settings()
        self.water = SimResource(
            self.settings,
            id=s.ContinuousResource(
                name="x",
                class_of_supply=201,
                environment="Unpressurized",
                packing_factor=0,
                unit_mass=1,
                unit_volume=0,
            ).id,
            name="Water",
            class_of_supply=201,
            unit_mass=2.0,
            unit_volume=0.002,
            packing_factor=0.5,
        )
        self.generic_water = SimResource.generic(self.settings, 201)
        self.generic_crew = SimResource.generic(self.settings, 2)

    def test_generic_resource(self):
        self.assertTrue(self.generic_water.is_generic)
        self.assertEqual(self.generic_water.unit_mass, 1)
        self.assertEqual(self.generic_water.unit_volume, 0.001)
        self.assertEqual(self.generic_crew.unit_volume, 0.007)
        self.assertEqual(self.generic_water.resource_type, "Generic")
        self.assertEqual(
            self.generic_water.name, "Generic COS 201 (Water and Support Equipment)"
        )

    def test_generic_packing_factor(self):
        gas = SimResource.generic(self.settings, 203)
        pressurized = SimResource.generic(self.settings, 4, "Pressurized")
        unpressurized = SimResource.generic(self.settings, 4, "Unpressurized")
        self.assertEqual(gas.packing_factor, 1.0)
        self.assertEqual(self.generic_water.packing_factor, 0.5)
        self.assertEqual(pressurized.packing_factor, 0.2)
        self.assertEqual(unpressurized.packing_factor, 0.6)

    def test_equality(self):
        self.assertEqual(self.generic_water, SimResource.generic(self.settings, 201))
        self.assertNotEqual(
            self.generic_water, SimResource.generic(self.settings, 201, "Pressurized")
        )
        self.assertNotEqual(self.generic_water, self.water)
        self.assertEqual(
            len({self.generic_water, SimResource.generic(self.settings, 201)}), 1
        )

    def test_substitution(self):
        # generic resources substitute for the same or a more general class
        self.assertTrue(self.generic_water.is_substitutable_for(self.generic_crew))
        self.assertTrue(self.generic_water.is_substitutable_for(self.generic_water))
        self.assertFalse(self.generic_crew.is_substitutable_for(self.generic_water))
        # specific resources only substitute for themselves
        self.assertTrue(self.water.is_substitutable_for(self.water))
        self.assertFalse(self.water.is_substitutable_for(self.generic_water))

    def test_demand_rounding(self):
        demand = Demand(self.water, 1.2345)
        self.assertAlmostEqual(demand.amount, 1.23)
        self.assertEqual(demand.raw_amount, 1.2345)
        self.assertAlmostEqual(demand.mass, 2.47)
        self.assertAlmostEqual(demand.volume, 0.002469)

    def test_demand_set_aggregates(self):
        demands = DemandSet([Demand(self.water, 1), Demand(self.generic_water, 2)])
        demands.add(Demand(self.water, 3))
        self.assertEqual(len(demands), 2)
        self.assertEqual(demands.get(self.water).amount, 4)
        self.assertAlmostEqual(demands.total_mass, 10)
        # ordered by class of supply with generic resources first
        self.assertEqual(
            [d.resource for d in demands], [self.generic_water, self.water]
        )

    def test_demand_set_does_not_retain_arguments(self):
        demand = Demand(self.water, 1)
        demands = DemandSet([demand])
        demands.get(self.water).amount = 5
        self.assertEqual(demand.amount, 1)

    def test_demand_set_remove_and_clean(self):
        demands = DemandSet([Demand(self.water, 5)])
        partial = Demand(self.water, 2)
        self.assertTrue(demands.remove(partial))
        self.assertEqual(partial.amount, 0)
        self.assertEqual(demands.get(self.water).amount, 3)
        excess = Demand(self.water, 4)
        self.assertFalse(demands.remove(excess))
        self.assertEqual(excess.amount, 1)
        demands.clean()
        self.assertEqual(len(demands), 0)


class TestElements(unittest.TestCase):
    def setUp(self):
        self.settings = Settings(s.Configuration(environment_constrained=True))
        self.water = SimResource.generic(self.settings, 201)
        self.food = SimResource.generic(self.settings, 202)

    def test_rounded_mass(self):
        element = SimElement(self.settings, name="e", mass=1.234)
        self.assertAlmostEqual(element.mass, 1.23)
        self.assertAlmostEqual(element.total_mass, 1.23)

    def test_environment_only_applies_if_constrained(self):
        element = SimElement(Settings(), name="e", environment="Pressurized")
        self.assertEqual(element.environment, s.Environment.UNPRESSURIZED)
        element = SimElement(self.settings, name="e", environment="Pressurized")
        self.assertEqual(element.environment, s.Environment.PRESSURIZED)

    def test_carrier_nested_mass_and_location(self):
        outer = SimCarrier(self.settings, name="outer", mass=100, max_cargo_mass=1000)
        inner = SimCarrier(self.settings, name="inner", mass=10, max_cargo_mass=100)
        payload = SimElement(self.settings, name="payload", mass=5, class_of_supply=601)
        self.assertTrue(outer.add(inner))
        self.assertTrue(inner.add(payload))
        self.assertEqual(outer.total_mass, 115)
        self.assertEqual(outer.cargo_mass, 15)
        self.assertEqual(outer.get_total_mass(s.ClassOfSupply.COS_6), 5)
        self.assertTrue(payload.is_inside(outer))
        self.assertIsNone(payload.location)
        self.assertEqual(outer.complete_contents, [inner, payload])

    def test_carrier_mass_capacity(self):
        carrier = SimCarrier(self.settings, name="c", max_cargo_mass=10)
        self.assertTrue(carrier.add(SimElement(self.settings, name="a", mass=6)))
        self.assertFalse(carrier.add(SimElement(self.settings, name="b", mass=6)))
        self.assertTrue(carrier.add(SimElement(self.settings, name="c", mass=4)))
        self.assertEqual(carrier.cargo_mass, 10)

    def test_carrier_parent_mass_capacity(self):
        outer = SimCarrier(self.settings, name="outer", max_cargo_mass=10)
        inner = SimCarrier(self.settings, name="inner", mass=5, max_cargo_mass=100)
        self.assertTrue(outer.add(inner))
        self.assertFalse(inner.add(SimElement(self.settings, name="a", mass=6)))
        self.assertTrue(inner.add(SimElement(self.settings, name="b", mass=5)))

    def test_carrier_crew_capacity(self):
        carrier = SimCarrier(self.settings, name="c", max_cargo_mass=0, max_crew_size=1)
        first = SimCrewMember(self.settings, name="a", mass=100)
        self.assertTrue(carrier.add(first))
        self.assertTrue(carrier.add(first))
        self.assertFalse(carrier.add(SimCrewMember(self.settings, name="b", mass=100)))
        self.assertEqual(carrier.crew_size, 1)
        # crew members do not count as cargo but do count towards total mass
        self.assertEqual(carrier.cargo_mass, 0)
        self.assertEqual(carrier.total_mass, 100)

    def test_carrier_environment_constraint(self):
        carrier = SimCarrier(self.settings, name="c", max_cargo_mass=10)
        pressurized = SimElement(self.settings, name="a", environment="Pressurized")
        self.assertFalse(carrier.add(pressurized))
        carrier.cargo_environment = s.Environment.PRESSURIZED
        self.assertTrue(carrier.add(pressurized))

    def test_carrier_cannot_contain_itself(self):
        outer = SimCarrier(self.settings, name="outer", max_cargo_mass=100)
        inner = SimCarrier(self.settings, name="inner", max_cargo_mass=100)
        outer.add(inner)
        self.assertFalse(inner.add(outer))
        self.assertFalse(outer.add(outer))

    def test_moving_between_carriers(self):
        first = SimCarrier(self.settings, name="a", max_cargo_mass=10)
        second = SimCarrier(self.settings, name="b", max_cargo_mass=10)
        element = SimElement(self.settings, name="e", mass=5)
        first.add(element)
        second.add(element)
        self.assertEqual(first.contents, ())
        self.assertIs(element.container, second)

    def test_resource_container_capacity(self):
        container = SimResourceContainer(
            self.settings, name="c", mass=1, max_cargo_mass=10
        )
        self.assertTrue(container.add(self.water, 6))
        self.assertFalse(container.add(self.water, 6))
        self.assertTrue(container.add(self.water, 4))
        self.assertEqual(container.total_mass, 11)
        self.assertEqual(container.get_total_mass(s.ClassOfSupply.COS_2), 10)
        self.assertFalse(container.remove(self.water, 11))
        self.assertTrue(container.remove(self.water, 4))
        self.assertTrue(container.remove(self.water, 6))
        self.assertEqual(container.contents, {})

    def test_resource_container_environment_constraint(self):
        container = SimResourceContainer(self.settings, name="c", max_cargo_mass=10)
        pressurized = SimResource.generic(self.settings, 202, "Pressurized")
        self.assertFalse(container.add(pressurized, 1))

    def test_resource_container_satisfies_consumption(self):
        container = SimResourceContainer(
            self.settings, name="c", max_cargo_mass=10, contents=[Demand(self.water, 5)]
        )
        demands = DemandSet(
            [Demand(SimResource.generic(self.settings, 2), 3), Demand(self.food, 1)]
        )
        container.satisfy_demands(demands, None)
        # generic water substitutes for the generic crew provisions demand
        self.assertEqual(container.get_amount(self.water), 2)
        self.assertEqual([d.resource for d in demands], [self.food])
        demands = DemandSet([Demand(self.water, 3)])
        container.satisfy_demands(demands, None)
        self.assertEqual(container.get_amount(self.water), 0)
        self.assertEqual(demands.get(self.water).amount, 1)

    def test_resource_container_satisfies_production(self):
        container = SimResourceContainer(
            self.settings, name="c", max_cargo_mass=10, contents=[Demand(self.water, 5)]
        )
        demands = DemandSet([Demand(self.water, -8)])
        container.satisfy_demands(demands, None)
        self.assertEqual(container.get_amount(self.water), 10)
        self.assertEqual(demands.get(self.water).amount, -3)

    def test_exploration_items_are_not_consumed(self):
        samples = SimResource.generic(self.settings, 603)
        container = SimResourceContainer(
            self.settings, name="c", max_cargo_mass=10, contents=[Demand(samples, 5)]
        )
        demands = DemandSet([Demand(samples, 3)])
        container.satisfy_demands(demands, None)
        self.assertEqual(len(demands), 0)
        self.assertEqual(container.get_amount(samples), 5)

    def test_resource_tank(self):
        tank = SimResourceTank(
            self.settings, name="t", resource=self.water, amount=5, max_amount=10
        )
        self.assertFalse(tank.add(self.food, 1))
        self.assertFalse(tank.add(self.water, 6))
        self.assertTrue(tank.add(self.water, 5))
        self.assertFalse(tank.remove(self.water, 11))
        self.assertTrue(tank.remove(self.water, 4))
        self.assertEqual(tank.amount, 6)
        self.assertEqual(tank.total_mass, 6)
        demands = DemandSet([Demand(self.water, 8)])
        tank.satisfy_demands(demands, None)
        self.assertEqual(tank.amount, 0)
        self.assertEqual(demands.get(self.water).amount, 2)

    def test_propulsive_vehicle_mass_includes_fuel(self):
        fuel = SimResource.generic(self.settings, 101)
        tank = SimResourceTank(self.settings, resource=fuel, amount=50, max_amount=60)
        rcs_tank = SimResourceTank(self.settings, resource=fuel, amount=5, max_amount=5)
        vehicle = SimPropulsiveVehicle(
            self.settings,
            name="v",
            mass=100,
            propulsion_systems=[
                SimPropulsionSystem("OMS", isp=300, fuel_tank=tank),
                SimPropulsionSystem("RCS", isp=200, fuel_tank=rcs_tank),
            ],
        )
        self.assertEqual(vehicle.total_mass, 155)
        self.assertEqual(vehicle.get_total_mass(s.ClassOfSupply.COS_1), 55)
        self.assertIs(vehicle.fuel_tank, tank)
        self.assertIs(vehicle.fuel_tank.container, vehicle)
        self.assertEqual(vehicle.fuel_tanks, [tank, rcs_tank])
        self.assertEqual(tank.name, "v OMS Fuel Tank")
        self.assertEqual(rcs_tank.name, "v RCS Fuel Tank")
        self.assertEqual(vehicle.get_propulsion_system(s.PropulsionType.RCS).isp, 200)
        demands = DemandSet([Demand(fuel, 20)])
        vehicle.satisfy_demands(demands, None)
        self.assertEqual(vehicle.fuel_tank.amount, 30)
        self.assertEqual(len(demands), 0)

    def test_propulsion_systems_share_fuel_tank(self):
        fuel = SimResource.generic(self.settings, 101)
        tank = SimResourceTank(self.settings, resource=fuel, amount=50, max_amount=60)
        vehicle = SimPropulsiveVehicle(
            self.settings,
            name="v",
            mass=100,
            propulsion_systems=[
                SimPropulsionSystem("OMS", isp=300, fuel_tank=tank),
                SimPropulsionSystem("RCS", isp=200, fuel_tank=tank),
            ],
        )
        self.assertEqual(vehicle.fuel_tanks, [tank])
        self.assertEqual(vehicle.total_mass, 150)
        self.assertEqual(tank.name, "v OMS Fuel Tank")


class TestState(unittest.TestCase):
    def test_instance_inherits_from_template(self):
        builder = ScenarioBuilder()
        template = s.ElementCarrier(
            name="Lander",
            mass=1000,
            max_cargo_mass=500,
            max_crew=2,
            class_of_supply=9023,
            states=[
                s.State(name="Active", type="Active"),
                s.State(name="Off", type="Quiescent"),
            ],
            current_state_index=1,
        )
        default = builder.add(template, s.InstElementCarrier)
        custom = builder.add(
            template,
            s.InstElementCarrier,
            name="Heavy",
            mass=2000,
            current_state_index=0,
        )
        state = State(builder.build())
        element = state.get_element(default.id)
        self.assertIsInstance(element, SimCarrier)
        self.assertEqual(element.name, "Lander")
        self.assertEqual(element.mass, 1000)
        self.assertEqual(element.max_cargo_mass, 500)
        self.assertEqual(element.max_crew_size, 2)
        self.assertEqual(element.class_of_supply, s.ClassOfSupply.COS_9023)
        self.assertEqual(element.current_state.name, "Off")
        element = state.get_element(custom.id)
        self.assertEqual(element.name, "Heavy")
        self.assertEqual(element.mass, 2000)
        self.assertEqual(element.current_state.name, "Active")
        # each instance has its own states
        self.assertIsNot(element.states[0], state.get_element(default.id).states[0])

    def test_vehicle_fuel(self):
        builder = ScenarioBuilder()
        stage = builder.vehicle(fuel=9000, isp=321)
        element = State(builder.build()).get_element(stage.id)
        self.assertIsInstance(element, SimPropulsiveVehicle)
        (system,) = element.propulsion_systems
        self.assertEqual(system.propulsion_type, s.PropulsionType.OMS)
        self.assertEqual(system.isp, 321)
        self.assertIs(system.fuel_tank, element.fuel_tank)
        self.assertEqual(element.fuel_tank.amount, 9000)
        self.assertEqual(element.fuel_tank.max_amount, 9000)
        self.assertEqual(element.fuel_tank.resource.name, "Fuel")
        self.assertEqual(element.total_mass, 10000)

    def test_nested_contents_and_initial_locations(self):
        builder = ScenarioBuilder()
        crew = builder.crew()
        carrier = builder.carrier()
        carrier.contents = [s.InstElementUUID(id=crew.id)]
        builder.lsp.contents = [s.InstElementUUID(id=carrier.id)]
        state = State(builder.build())
        self.assertEqual(state.get_element(crew.id).location.name, "LSP")
        self.assertEqual(len(state.network.registrar), 2)
        self.assertEqual(state.get_location(builder.lsp.id).total_crew_size, 1)

    def test_network(self):
        builder = ScenarioBuilder()
        state = State(builder.build())
        edge = state.get_location(builder.ksc_leo.id)
        self.assertEqual(edge.origin.name, "KSC")
        self.assertEqual(edge.destination.name, "LEO")
        self.assertEqual(edge.duration, 0.25)
        self.assertEqual(edge.burns[0].delta_v, 1000)
        self.assertTrue(state.get_location(builder.lsp.id).is_exploration_site)
        self.assertFalse(state.get_location(builder.ksc.id).is_exploration_site)
        self.assertIsNone(state.get_location(builder.burn.id))

    def test_unknown_references_are_rejected(self):
        builder = ScenarioBuilder()
        carrier = builder.carrier()
        ghost = s.InstElement(name="Ghost", template_id=carrier.template_id)
        builder.mission([builder.create([ghost], builder.ksc)])
        with self.assertRaisesRegex(ValueError, "unknown element"):
            State(builder.build())

    def test_time_conversion(self):
        builder = ScenarioBuilder()
        builder.mission([], days=10.5)
        state = State(builder.build())
        self.assertEqual(state.missions[0].start_time, 10.5)
        self.assertEqual(state.get_date(10.5), state.missions[0].start_date)


class TestDemandModels(unittest.TestCase):
    def test_rated_and_impulse_demand_models(self):
        builder = ScenarioBuilder()
        rated = s.RatedDemandModel(
            name="Rated",
            demands=[
                s.ResourceAmountRate(resource=builder.water.id, rate=2.0),
                s.GenericResourceAmountRate(
                    class_of_supply=202, environment="Unpressurized", rate=0.004
                ),
            ],
        )
        impulse = s.TimedImpulseDemandModel(
            name="Impulse",
            demands=[s.ResourceAmount(resource=builder.water.id, amount=7)],
        )
        builder.demand_models = [rated, impulse]
        element = builder.add(
            s.Element(
                name="Habitat",
                states=[
                    s.State(
                        name="Active",
                        type="Active",
                        demand_models=[
                            s.InstRatedDemandModel(name="Rated", template_id=rated.id),
                            s.InstTimedImpulseDemandModel(
                                name="Impulse", template_id=impulse.id
                            ),
                        ],
                    )
                ],
                current_state_index=0,
            ),
            s.InstElement,
        )
        state = State(builder.build())
        sim_element = state.get_element(element.id)
        demands = sim_element.generate_demands(10, None)
        self.assertEqual(demands.get(state.get_resource(builder.water.id)).amount, 27)
        # small rates are not rounded before multiplying by the duration
        self.assertAlmostEqual(demands.get(state.get_resource(202)).amount, 0.04)
        # the impulse demand is only generated once
        demands = sim_element.generate_demands(10, None)
        self.assertEqual(demands.get(state.get_resource(builder.water.id)).amount, 20)

    def test_instance_overrides_template_demands(self):
        builder = ScenarioBuilder()
        rated = s.RatedDemandModel(
            name="Rated",
            demands=[s.ResourceAmountRate(resource=builder.water.id, rate=2)],
        )
        builder.demand_models = [rated]
        element = builder.add(
            s.Element(
                name="Habitat",
                states=[
                    s.State(
                        name="Active",
                        type="Active",
                        demand_models=[
                            s.InstRatedDemandModel(
                                name="Rated",
                                template_id=rated.id,
                                demands=[
                                    s.ResourceAmountRate(
                                        resource=builder.water.id, rate=5
                                    )
                                ],
                            )
                        ],
                    )
                ],
                current_state_index=0,
            ),
            s.InstElement,
        )
        state = State(builder.build())
        demands = state.get_element(element.id).generate_demands(2, None)
        self.assertEqual(demands.get(state.get_resource(builder.water.id)).amount, 10)

    def _build_sparing(self, parts_list_enabled, parts=None):
        builder = ScenarioBuilder()
        sparing = s.SparingByMassDemandModel(
            name="Sparing",
            unpressurized_spares_rate=0.05,
            pressurized_spares_rate=0.10,
            parts_list_enabled=parts_list_enabled,
        )
        builder.demand_models = [sparing]
        element = builder.add(
            s.Element(
                name="Habitat",
                mass=7300,
                parts=parts(builder) if parts else [],
                states=[
                    s.State(
                        name="Active",
                        type="Active",
                        demand_models=[
                            s.InstSparingByMassDemandModel(
                                name="Sparing", template_id=sparing.id
                            )
                        ],
                    )
                ],
                current_state_index=0,
            ),
            s.InstElement,
        )
        state = State(builder.build())
        return builder, state, state.get_element(element.id)

    def test_sparing_by_mass_without_parts(self):
        _, state, element = self._build_sparing(False)
        demands = element.generate_demands(365, None)
        unpressurized = state.get_resource(4, "Unpressurized")
        pressurized = state.get_resource(4, "Pressurized")
        self.assertAlmostEqual(demands.get(unpressurized).amount, 365)
        self.assertAlmostEqual(demands.get(pressurized).amount, 730)

    def test_sparing_by_mass_with_parts(self):
        builder, state, element = self._build_sparing(
            True,
            lambda b: [
                s.Part(
                    resource=b.spare.id,
                    quantity=100,
                    mean_time_to_repair=timedelta(hours=2),
                    mass_to_repair=1,
                )
            ],
        )
        self.assertEqual(element.parts[0].mean_time_to_repair, 2)
        self.assertEqual(element.parts[0].unit_mean_time_to_repair, 0.4)
        demands = element.generate_demands(365, None)
        # 100 unpressurized parts of 5 kg leave 6800 kg of generic parts
        spare = state.get_resource(builder.spare.id)
        self.assertAlmostEqual(demands.get(spare).amount, 0.05 * 7300 * 100 / 7300)
        self.assertAlmostEqual(
            demands.get(state.get_resource(4, "Unpressurized")).amount,
            0.05 * 7300 * 6800 / 7300,
        )
        self.assertAlmostEqual(
            demands.get(state.get_resource(4, "Pressurized")).amount, 0.10 * 7300
        )

    def test_sparing_by_mass_of_massless_element(self):
        builder = ScenarioBuilder()
        sparing = s.SparingByMassDemandModel(
            name="Sparing",
            unpressurized_spares_rate=0.05,
            pressurized_spares_rate=0.10,
            parts_list_enabled=True,
        )
        builder.demand_models = [sparing]
        element = builder.add(
            s.Element(
                name="Massless",
                states=[
                    s.State(
                        name="Active",
                        type="Active",
                        demand_models=[
                            s.InstSparingByMassDemandModel(
                                name="Sparing", template_id=sparing.id
                            )
                        ],
                    )
                ],
                current_state_index=0,
            ),
            s.InstElement,
        )
        state = State(builder.build())
        demands = state.get_element(element.id).generate_demands(365, None)
        demands.clean()
        self.assertEqual(len(demands), 0)

    def test_crew_consumables(self):
        builder = ScenarioBuilder()
        consumables = s.CrewConsumablesDemandModel(name="Consumables")
        builder.demand_models = [consumables]
        crew = [builder.crew("A"), builder.crew("B")]
        lander = builder.carrier("Lander", mass=1000, max_cargo_mass=1000)
        builder.mission(
            [
                builder.create([lander], builder.ksc),
                builder.create(crew, lander, location=builder.ksc, priority=2),
                builder.flight([lander], builder.ksc_lsp, priority=3),
                s.CrewedEVA(
                    name="EVA",
                    priority=1,
                    mission_time=timedelta(days=4),
                    location=builder.lsp.id,
                    vehicle=lander.id,
                    eva_duration=timedelta(hours=6),
                    element_states=[
                        s.ElementState(element=c.id, state_index=-1) for c in crew
                    ],
                    additional_demands=[],
                ),
                builder.flight([lander], builder.lsp_ksc, days=10),
            ],
            demand_models=[
                s.InstCrewConsumablesDemandModel(
                    name="Consumables", template_id=consumables.id, reserves_duration=2
                )
            ],
            return_origin=builder.lsp.id,
            return_destination=builder.ksc.id,
        )
        simulator = FullSimulator(builder.build())
        simulator.simulate()
        mission = simulator.state.missions[0]
        self.assertEqual(mission.crew_size, 2)
        self.assertTrue(mission.is_crewed)
        self.assertEqual(mission.number_eva, 1)
        self.assertEqual(mission.eva_crew_time, 12)
        self.assertEqual(mission.duration, 13)
        self.assertEqual(mission.transit_duration, 3)
        self.assertEqual(mission.destination_duration, 7)
        self.assertEqual(mission.return_transit_duration, 3)
        self.assertEqual(mission.dormant_duration, 0)

        # 7 days at the destination, 6 days in transit, 2 days of reserves
        crew_days, reserve_crew_days, eva = 13 * 2, 15 * 2, 12
        expected = {
            201: reserve_crew_days * 3.6 * (1 - 0.42) + eva * 0.6875,
            202: reserve_crew_days * (0.05556 + 0.76389 + 1.61667),
            203: reserve_crew_days * (3.85714 + 2.21429) + eva * 0.07875,
            204: reserve_crew_days * 0.27778 + 1.8 * 2,
            205: crew_days * 2.3 / 4,
            206: 10 * 2,
            301: 5 * 2,
            302: 107 * 2 + 0.3625 * eva,
            303: 20 + 0.1 * 2,
            304: 25,
            305: 20,
            306: 5 * 2,
            701: crew_days * 0.05,
            702: reserve_crew_days * 0.05,
        }
        demands = simulator.get_demands(mission, mission_level=True)
        self.assertEqual(len(demands), len(expected))
        for class_of_supply, amount in expected.items():
            demand = demands.get(simulator.state.get_resource(class_of_supply))
            self.assertAlmostEqual(demand.amount, amount, delta=0.03)
        # mission demands occur upon arrival at the destination
        history = simulator.get_demand_history(mission)
        self.assertEqual([d.time for d in history], [3])
        self.assertEqual(history[0].location.name, "LSP")
        self.assertIsNone(history[0].element)
        self.assertAlmostEqual(
            simulator.get_demands(
                mission, class_of_supply=s.ClassOfSupply.COS_3
            ).total_mass,
            sum(v for k, v in expected.items() if 300 < k < 400),
            delta=0.05,
        )


if __name__ == "__main__":
    unittest.main()
