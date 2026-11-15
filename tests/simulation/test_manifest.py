"""
Tests of the manifest: packing demands in containers and loading containers
in the carriers of transports.
"""

import unittest
from datetime import timedelta

from spacenet import schemas as s
from spacenet.simulation import (
    DemandSimulator,
    FullSimulator,
    ManifestResult,
    ManifestSelection,
    SimManifest,
    container_factory,
)
from spacenet.simulation.analysis import export_manifest
from spacenet.simulation.settings import Settings

from .util import START, ScenarioBuilder, load_scenario

CTB = s.ManifestContainerType.CTB


def unsatisfied_mass(simulator):
    """Gets the total mass of the unsatisfied demands of a simulator."""
    return sum(d.demands.total_mass for d in simulator.unsatisfied_demands)


def build(amounts, max_cargo_mass=5000, crew_rate=0, **configuration):
    """
    Builds a scenario with one flight (departing on day 0, arriving on day 3)
    of a lander (and a crew member) from KSC to LSP. The mission demands the
    given amounts at LSP and the crew member demands a rate (kg per day) of
    generic crew provisions.
    """
    builder = ScenarioBuilder(**configuration)
    impulse = s.TimedImpulseDemandModel(name="Supplies", demands=amounts)
    rated = s.RatedDemandModel(
        name="Provisions",
        demands=[
            s.GenericResourceAmountRate(
                class_of_supply=2, environment="Unpressurized", rate=crew_rate
            )
        ],
    )
    builder.demand_models = [impulse, rated]
    lander = builder.carrier("Lander", max_cargo_mass=max_cargo_mass)
    crew = builder.add(
        s.HumanAgent(
            name="Crew",
            mass=100,
            active_time_fraction=0.5,
            states=[
                s.State(
                    name="Active",
                    type="Active",
                    demand_models=(
                        [
                            s.InstRatedDemandModel(
                                name="Provisions", template_id=rated.id
                            )
                        ]
                        if crew_rate
                        else []
                    ),
                )
            ],
            current_state_index=0,
        ),
        s.InstHumanAgent,
    )
    builder.mission(
        [
            builder.create([lander], builder.ksc),
            builder.create([crew], lander, location=builder.ksc, priority=2),
            builder.flight([lander], builder.ksc_lsp, priority=3),
        ],
        demand_models=(
            [s.InstTimedImpulseDemandModel(name="Supplies", template_id=impulse.id)]
            if amounts
            else []
        ),
    )
    return builder, lander


def generic(class_of_supply, amount, environment="Unpressurized"):
    """Makes an amount of a generic resource."""
    return s.GenericResourceAmount(
        class_of_supply=class_of_supply, environment=environment, amount=amount
    )


def find(manifest, class_of_supply):
    """Finds the aggregated demand for a class of supply."""
    return next(
        d
        for d in manifest.demands
        if int(d.resource.class_of_supply) == class_of_supply
    )


class TestContainerFactory(unittest.TestCase):
    def test_standard_containers(self):
        settings = Settings(s.Configuration(cargo_transfer_bag_max_mass=30))
        ctb = container_factory(settings, CTB)
        self.assertEqual(ctb.max_cargo_mass, 30)
        self.assertEqual(ctb.mass, 0.83)
        half = container_factory(settings, s.ManifestContainerType.HALF_CTB)
        self.assertEqual(half.max_cargo_mass, 15)
        double = container_factory(settings, s.ManifestContainerType.DOUBLE_CTB)
        self.assertEqual(double.max_cargo_mass, 60)
        small = container_factory(
            settings, s.ManifestContainerType.LIQUID_TANK_DERIVATIVE
        )
        large = container_factory(settings, s.ManifestContainerType.LIQUID_TANK)
        self.assertEqual(small.mass, 11.4567)
        self.assertEqual(small.max_cargo_mass, 24.9333)
        self.assertEqual(large.max_cargo_mass, 74.8)
        small = container_factory(settings, s.ManifestContainerType.GAS_TANK_DERIVATIVE)
        large = container_factory(settings, s.ManifestContainerType.GAS_TANK)
        self.assertEqual(small.max_cargo_volume, 0.275)
        self.assertEqual(large.max_cargo_mass, 100)
        shoss = container_factory(settings, s.ManifestContainerType.SHOSS)
        self.assertEqual((shoss.mass, shoss.max_cargo_mass), (120, 200))
        pressurized = container_factory(
            settings, s.ManifestContainerType.PRESSURIZED_SHOSS
        )
        self.assertEqual(pressurized.cargo_environment, s.Environment.PRESSURIZED)

    def test_misspelled_configuration_names_are_accepted(self):
        configuration = s.Configuration.model_validate(
            {"smallGasTTankMaxVolume": 0.5, "smallLiquidTTankMass": 12}
        )
        self.assertEqual(configuration.small_gas_tank_max_volume, 0.5)
        self.assertEqual(configuration.small_liquid_tank_mass, 12)


class TestPacking(unittest.TestCase):
    def test_imports_aggregated_demands(self):
        builder, _ = build([generic(2, 60), generic(6, 30)])
        manifest = SimManifest.create(builder.build())
        self.assertEqual(len(manifest.edges), 1)
        self.assertEqual(len(manifest.points), 1)
        self.assertEqual([d.amount for d in manifest.demands], [60, 30])
        self.assertFalse(any(d.is_edge_demand for d in manifest.demands))
        self.assertEqual(manifest.demands[0].point.node.name, "LSP")
        self.assertEqual(manifest.demands[0].point.time, 3)

    def test_pack_and_unpack(self):
        builder, _ = build([generic(2, 60)])
        manifest = SimManifest.create(builder.build())
        demand = manifest.demands[0]
        container = manifest.add_container(CTB)
        self.assertEqual(container.name, "CTB 1")
        self.assertIsNone(manifest.get_current_supply_point(container))
        self.assertEqual(manifest.get_empty_containers(), [container])
        self.assertTrue(manifest.can_pack_demand(demand, container))
        self.assertAlmostEqual(manifest.pack_demand(demand, container), 26.8)
        self.assertAlmostEqual(manifest.get_packed_amount(demand), 26.8)
        self.assertAlmostEqual(manifest.get_remaining_amount(demand), 33.2)
        self.assertAlmostEqual(manifest.get_container_cargo_mass(container), 26.8)
        self.assertIs(manifest.get_current_supply_point(container), demand.point)
        # a full container cannot pack more
        self.assertFalse(manifest.can_pack_demand(demand, container))
        self.assertEqual(manifest.pack_demand(demand, container), 0)
        self.assertTrue(manifest.can_unpack_demand(demand))
        self.assertTrue(manifest.can_unpack_demand(demand, container))
        manifest.unpack_demand(demand, container)
        self.assertEqual(manifest.get_packed_amount(demand), 0)
        self.assertFalse(manifest.can_unpack_demand(demand))
        self.assertEqual(manifest.add_container(CTB).name, "CTB 2")

    def test_partial_demand_fits_in_partly_filled_container(self):
        builder, _ = build([generic(2, 20), generic(3, 20)])
        manifest = SimManifest.create(builder.build())
        container = manifest.add_container(CTB)
        manifest.pack_demand(find(manifest, 2), container)
        # NOTE: differs from the reference implementation
        self.assertTrue(manifest.can_pack_demand(find(manifest, 3), container))
        self.assertAlmostEqual(manifest.pack_demand(find(manifest, 3), container), 6.8)

    def test_volume_constraint(self):
        builder, _ = build([generic(2, 60)], volume_constrained=True)
        manifest = SimManifest.create(builder.build())
        container = manifest.add_container(CTB)
        # generic crew provisions occupy 0.007 m^3/kg and a bag holds 0.049 m^3
        self.assertAlmostEqual(manifest.pack_demand(manifest.demands[0], container), 7)

    def test_environment_constraint(self):
        builder, _ = build(
            [generic(2, 10, "Pressurized")], environment_constrained=True
        )
        manifest = SimManifest.create(builder.build())
        demand = manifest.demands[0]
        container = manifest.add_container(CTB)
        self.assertFalse(manifest.can_pack_demand(demand, container))
        self.assertEqual(manifest.pack_demand(demand, container), 0)
        pressurized = manifest.add_container(s.ManifestContainerType.PRESSURIZED_SHOSS)
        self.assertTrue(manifest.can_pack_demand(demand, pressurized))

    def test_remove_container(self):
        builder, lander = build([generic(2, 20)])
        manifest = SimManifest.create(builder.build())
        container = manifest.add_container(CTB)
        manifest.pack_demand(manifest.demands[0], container)
        edge = manifest.edges[0]
        carrier = manifest.get_carrier(edge, lander.id)
        self.assertTrue(manifest.manifest_container(container, edge, carrier))
        manifest.remove_container(container)
        self.assertEqual(manifest.containers, [])
        self.assertEqual(manifest.get_loaded_containers(edge, lander.id), [])
        self.assertEqual(manifest.get_packed_amount(manifest.demands[0]), 0)


class TestAutoPack(unittest.TestCase):
    def _auto_pack(self, amounts, **configuration):
        builder, _ = build(amounts, **configuration)
        manifest = SimManifest.create(builder.build())
        for demand in manifest.demands:
            manifest.auto_pack_demand(demand)
        return builder, manifest

    def _types(self, manifest):
        return [c.container_type.value for c in manifest.containers]

    def test_crew_provisions_use_cargo_transfer_bags(self):
        _, manifest = self._auto_pack([generic(2, 60)])
        self.assertEqual(self._types(manifest), ["Cargo Transfer Bag"] * 3)
        self.assertEqual(
            [
                round(manifest.get_container_cargo_mass(c), 2)
                for c in manifest.containers
            ],
            [26.8, 26.8, 6.4],
        )
        self.assertEqual(manifest.get_remaining_amount(manifest.demands[0]), 0)

    def test_existing_bags_are_filled_first(self):
        _, manifest = self._auto_pack([generic(2, 30), generic(4, 20)])
        # 30 kg fill one bag and 3.2 kg of a second which also holds 20 kg
        self.assertEqual(len(manifest.containers), 2)
        self.assertAlmostEqual(
            manifest.get_container_cargo_mass(manifest.containers[1]), 23.2
        )

    def test_water_uses_liquid_tanks(self):
        builder, _ = build([])
        water = s.ResourceAmount(resource=builder.water.id, amount=90)
        builder, _ = build([water])
        # the amount must reference the water of the rebuilt scenario
        water.resource = builder.water.id
        manifest = SimManifest.create(builder.build())
        manifest.auto_pack_demand(manifest.demands[0])
        self.assertEqual(
            self._types(manifest), ["Liquid Tank", "Liquid Tank Derivative"]
        )
        self.assertAlmostEqual(
            manifest.get_container_cargo_mass(manifest.containers[0]), 74.8
        )
        self.assertAlmostEqual(
            manifest.get_container_cargo_mass(manifest.containers[1]), 15.2
        )

    def test_gases_use_gas_tanks(self):
        _, manifest = self._auto_pack([generic(203, 105)])
        self.assertEqual(self._types(manifest), ["Gas Tank", "Gas Tank Derivative"])

    def test_propellant_uses_liquid_tanks(self):
        _, manifest = self._auto_pack([generic(1, 20)])
        self.assertEqual(self._types(manifest), ["Liquid Tank Derivative"])

    def test_stowage_is_ignored(self):
        _, manifest = self._auto_pack([generic(5, 20)])
        self.assertEqual(manifest.containers, [])

    def test_exploration_items_use_a_custom_container(self):
        _, manifest = self._auto_pack([generic(6, 30), generic(8, 10)])
        science, infrastructure = manifest.containers
        self.assertEqual(science.name, "Science 1")
        self.assertEqual(science.max_cargo_mass, 30)
        # unpressurized generic resources require 0.6 kg of packing per kg
        self.assertAlmostEqual(science.mass, 18)
        self.assertEqual(infrastructure.name, "Infrastructure 1")
        self.assertEqual(manifest.get_remaining_amount(manifest.demands[0]), 0)

    def test_containers_take_the_environment_of_the_resource(self):
        _, manifest = self._auto_pack(
            [generic(2, 10, "Pressurized"), generic(3, 10)],
            environment_constrained=True,
        )
        self.assertEqual(
            [c.cargo_environment.value for c in manifest.containers],
            ["Pressurized", "Unpressurized"],
        )


class TestManifesting(unittest.TestCase):
    def test_load_and_unload(self):
        builder, lander = build([generic(2, 60)], max_cargo_mass=50)
        manifest = SimManifest.create(builder.build())
        manifest.auto_pack_demand(manifest.demands[0])
        edge = manifest.edges[0]
        carrier = manifest.get_carrier(edge, lander.id)
        first, second, third = manifest.containers
        self.assertFalse(manifest.can_manifest_container(first, None, carrier))
        self.assertTrue(manifest.can_manifest_container(first, edge, carrier))
        self.assertTrue(manifest.manifest_container(first, edge, carrier))
        self.assertTrue(manifest.is_manifested(first, edge.point))
        # a loaded container cannot be loaded again or packed
        self.assertFalse(manifest.can_manifest_container(first, edge, carrier))
        self.assertFalse(manifest.can_pack_demand(manifest.demands[0], first))
        # crew members do not count as cargo
        self.assertAlmostEqual(
            manifest.get_carrier_cargo_mass(carrier, edge.point), 27.63
        )
        # a second bag exceeds the 50 kg capacity of the lander
        self.assertFalse(manifest.can_manifest_container(second, edge, carrier))
        self.assertTrue(manifest.can_unmanifest_container(first, edge))
        manifest.unmanifest_container(first, edge)
        self.assertEqual(manifest.get_loaded_containers(edge, lander.id), [])
        self.assertFalse(manifest.can_unmanifest_container(third, edge))

    def test_flight_capacity_limits_loads(self):
        builder, lander = build([generic(2, 60)])
        builder.ksc_lsp.max_cargo = 1130  # 1000 kg lander and 100 kg crew
        manifest = SimManifest.create(builder.build())
        manifest.auto_manifest()
        edge = manifest.edges[0]
        # NOTE: differs from the reference implementation
        self.assertEqual(len(manifest.get_loaded_containers(edge, lander.id)), 1)
        self.assertAlmostEqual(manifest.get_net_cargo_mass(edge), 30 - 27.63)

    def test_auto_manifest_satisfies_demands(self):
        builder, lander = build([generic(2, 60), generic(6, 30), generic(203, 5)])
        scenario = builder.build()
        manifest = SimManifest.create(scenario)
        manifest.auto_manifest()
        edge = manifest.edges[0]
        self.assertTrue(
            all(manifest.get_remaining_amount(d) == 0 for d in manifest.demands)
        )
        self.assertEqual(
            len(manifest.get_loaded_containers(edge, lander.id)),
            len(manifest.containers),
        )
        self.assertEqual(len(manifest.containers), 5)

        baseline = FullSimulator(scenario)
        baseline.simulate()
        self.assertAlmostEqual(unsatisfied_mass(baseline), 95)
        stored = manifest.to_schema()
        simulator = FullSimulator(scenario.model_copy(update={"manifest": stored}))
        simulator.simulate()
        self.assertEqual(simulator.errors, [])
        self.assertEqual(simulator.warnings, [])
        # the containers arrive in the lander
        final = simulator.network_history[-1].get_elements(builder.lsp.id)
        self.assertEqual(
            sorted(c.name for c in final[0].contents if c.is_container),
            sorted(c.name for c in manifest.containers),
        )
        # demands of other simulators do not depend on the manifest
        demands = DemandSimulator(
            scenario.model_copy(update={"manifest": stored}), demands_satisfied=False
        )
        demands.simulate()
        self.assertAlmostEqual(unsatisfied_mass(demands), 95)

    def test_manifest_round_trip(self):
        builder, _ = build([generic(2, 60), generic(6, 30)])
        scenario = builder.build()
        manifest = SimManifest.create(scenario)
        manifest.auto_manifest()
        stored = s.Manifest.model_validate_json(
            manifest.to_schema().model_dump_json(by_alias=True)
        )
        restored = SimManifest.create(scenario, stored)
        self.assertEqual(restored.dropped, [])
        self.assertEqual(restored.to_schema(), stored)
        # the scenario with its manifest can be serialized
        scenario = scenario.model_copy(update={"manifest": stored})
        loaded = s.Scenario.model_validate_json(scenario.model_dump_json(by_alias=True))
        self.assertEqual(loaded.manifest, stored)

    def test_stale_entries_are_dropped(self):
        builder, _ = build([generic(2, 60)])
        scenario = builder.build()
        manifest = SimManifest.create(scenario)
        manifest.auto_manifest()
        stored = manifest.to_schema()
        # delaying the mission changes the supply edge and supply point
        builder.missions[0].start_date = START + timedelta(days=10)
        restored = SimManifest.create(builder.build(), stored)
        self.assertGreater(len(restored.dropped), 0)
        self.assertEqual(len(restored.containers), 3)
        self.assertTrue(all(not c.items for c in restored.containers))
        self.assertEqual(restored.to_schema().loads, [])
        # the simulator skips loads which do not match the scenario
        stale = builder.build().model_copy(update={"manifest": stored})
        simulator = FullSimulator(stale)
        simulator.simulate()
        self.assertEqual(simulator.spatial_errors, [])

    def test_reset(self):
        builder, _ = build([generic(2, 60)])
        manifest = SimManifest.create(builder.build())
        manifest.auto_manifest()
        manifest.reset()
        self.assertEqual(manifest.to_schema(), s.Manifest())

    def test_edge_demands_travel_on_their_transport(self):
        builder, lander = build([], crew_rate=2)
        scenario = builder.build()
        manifest = SimManifest.create(scenario)
        (demand,) = manifest.demands
        self.assertTrue(demand.is_edge_demand)
        self.assertAlmostEqual(demand.amount, 6)
        manifest.auto_manifest()
        (container,) = manifest.containers
        self.assertEqual(
            manifest.get_loaded_containers(demand.edge, lander.id), [container]
        )
        self.assertFalse(manifest.is_edge_demand_container(container))
        stored = manifest.to_schema()
        self.assertIsNotNone(stored.containers[0].contents[0].edge_demand)
        self.assertEqual(SimManifest.create(scenario, stored).to_schema(), stored)
        baseline = FullSimulator(scenario)
        baseline.simulate()
        self.assertAlmostEqual(unsatisfied_mass(baseline), 6)
        simulator = FullSimulator(scenario.model_copy(update={"manifest": stored}))
        simulator.simulate()
        self.assertEqual(simulator.errors, [])

    def test_view_and_export(self):
        builder, lander = build([generic(2, 60)])
        manifest = SimManifest.create(builder.build())
        container = manifest.add_container(CTB)
        edge = manifest.edges[0]
        result = ManifestResult.create(
            manifest,
            ManifestSelection(
                container_id=container.id,
                edge_key=manifest.get_edge_key(edge),
                carrier_id=lander.id,
            ),
        )
        self.assertTrue(result.view.demands[0].can_pack)
        self.assertTrue(result.view.demands[0].can_auto_pack)
        self.assertFalse(result.view.containers[0].can_manifest)  # empty
        manifest.auto_manifest()
        result = ManifestResult.create(manifest)
        self.assertEqual(result.view.loaded_container_count, 3)
        self.assertAlmostEqual(result.view.packed_mass, 60)
        self.assertEqual(len(result.view.edges[0].carriers[0].containers), 3)
        self.assertEqual(len(export_manifest(manifest, "demands").splitlines()), 4)
        self.assertEqual(len(export_manifest(manifest, "containers").splitlines()), 4)
        self.assertEqual(
            len(export_manifest(manifest, "carriers", ";").splitlines()), 2
        )
        self.assertEqual(len(export_manifest(manifest, "edges", "\t").splitlines()), 2)
        with self.assertRaises(ValueError):
            export_manifest(manifest, "unknown")


class TestQuickStartManifest(unittest.TestCase):
    def test_scenarios_without_demands_have_an_empty_manifest(self):
        for path in (
            "quick_start/completed_quick_start_1_w_db.json",
            "artemis/artemis_campaign.json",
        ):
            manifest = SimManifest.create(load_scenario(path))
            manifest.auto_manifest()
            self.assertEqual(manifest.to_schema(), s.Manifest())

    def test_quick_start_2(self):
        scenario = load_scenario("quick_start/completed_quick_start_2_w_db.json")
        manifest = SimManifest.create(scenario)
        self.assertEqual(len(manifest.demands), 30)
        manifest.auto_manifest()
        for demand in manifest.demands:
            self.assertEqual(manifest.get_remaining_amount(demand), 0)
        precision = scenario.configuration.mass_precision
        for edge in manifest.edges:
            self.assertGreater(manifest.get_net_cargo_mass(edge), -precision)
            for carrier in edge.all_carriers:
                self.assertLess(
                    manifest.get_carrier_cargo_mass(carrier, edge.point),
                    carrier.max_cargo_mass + precision,
                )
        stored = manifest.to_schema()
        self.assertEqual(SimManifest.create(scenario, stored).to_schema(), stored)
        baseline = FullSimulator(scenario)
        baseline.simulate()
        simulator = FullSimulator(scenario.model_copy(update={"manifest": stored}))
        simulator.simulate()
        self.assertEqual(simulator.spatial_errors, [])
        self.assertEqual(simulator.warnings, [])
        self.assertLess(unsatisfied_mass(simulator), unsatisfied_mass(baseline))
