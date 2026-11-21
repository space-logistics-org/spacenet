"""
Tests of simulators.
"""

import unittest
from datetime import timedelta

from spacenet import schemas as s
from spacenet.simulation import (
    AggregatedDemandsAnalysis,
    DemandSimulator,
    FullSimulator,
    MiniSimulator,
    PreSimulator,
    RawDemandsAnalysis,
    Simulator,
)
from spacenet.simulation.events import DemandEvent, MoveEvent
from spacenet.simulation.records import (
    CREW_TIME_CORRECTIVE_MAINTENANCE,
    CREW_TIME_EXPLORATION,
    CREW_TIME_UNAVAILABLE,
    NetworkSnapshot,
)

from .util import ScenarioBuilder, load_scenario


class SnapshotSimulator(FullSimulator):
    """Full simulator which also records complete network snapshots."""

    def simulate(self):
        self.snapshots = []
        super().simulate()

    def _record_network(self):
        super()._record_network()
        self.snapshots.append(NetworkSnapshot.create(self.time, self.state.network))


class TestNetworkHistory(unittest.TestCase):
    SCENARIOS = (
        "quick_start/completed_quick_start_1_w_db.json",
        "quick_start/completed_quick_start_2_w_db.json",
        "quick_start/completed_quick_start_3_wo_db.json",
        "artemis/artemis_add_campaign.json",
    )

    def test_reconstructs_snapshots(self):
        for path in self.SCENARIOS:
            with self.subTest(path=path):
                simulator = SnapshotSimulator(load_scenario(path))
                simulator.simulate()
                history = simulator.network_history
                self.assertEqual(len(history), len(simulator.snapshots))
                self.assertEqual(list(history), simulator.snapshots)
                self.assertEqual(history[-1], simulator.snapshots[-1])
                self.assertEqual(history[1:3], simulator.snapshots[1:3])

    def test_records_only_changes(self):
        simulator = FullSimulator(load_scenario("artemis/artemis_add_campaign.json"))
        simulator.simulate()
        history = simulator.network_history
        changes = sum(len(frame.changed) for frame in history.frames)
        states = sum(len(state) for _, state in history.states())
        # most elements do not change at most time steps
        self.assertLess(changes, states / 3)
        with self.assertRaises(IndexError):
            history[len(history)]


def final_locations(simulator):
    """Maps the name of each remaining element to the name of its location."""
    return {
        " ".join(e.name.split()): e.location.name
        for e in simulator.state.network.elements
    }


class TestEventQueue(unittest.TestCase):
    def test_events_ordered_by_time_priority_and_name(self):
        simulator = MiniSimulator(ScenarioBuilder().build())
        simulator.initialize_simulation()
        events = [
            MoveEvent(name="d", time=2, priority=1),
            MoveEvent(name="c", time=1, priority=2),
            MoveEvent(name="b", time=1, priority=1),
            MoveEvent(name="a", time=1, priority=1),
            MoveEvent(name="e", time=1.01, priority=5),
        ]
        for event in events:
            simulator.schedule(event)
        order = []
        while simulator._peek_event() is not None:  # pylint: disable=protected-access
            simulator._next_event()  # pylint: disable=protected-access
            order.append((simulator.event.name, simulator.time))
        # times are rounded to the time precision of 0.05 days
        self.assertEqual(order, [("a", 1), ("b", 1), ("c", 1), ("e", 1), ("d", 2)])

    def test_base_simulator_is_abstract(self):
        with self.assertRaises(NotImplementedError):
            Simulator(ScenarioBuilder().build()).simulate()


class TestFullSimulator(unittest.TestCase):
    def setUp(self):
        self.builder = b = ScenarioBuilder()
        self.lander = b.carrier("Lander", mass=4000, max_cargo_mass=1000)
        self.crew = [b.crew("A"), b.crew("B")]
        self.science = b.element("Science", mass=300, class_of_supply=601)
        self.power = b.element("Power", mass=200, class_of_supply=803)
        b.mission(
            [
                b.create([self.lander], b.ksc),
                b.create(
                    [*self.crew, self.science, self.power],
                    self.lander,
                    location=b.ksc,
                    priority=2,
                ),
                b.flight([self.lander], b.ksc_lsp, priority=3),
                b.move([self.science, self.power], b.lsp, b.lsp, days=3),
                b.flight([self.lander], b.lsp_ksc, days=10),
            ],
            return_origin=b.lsp.id,
            return_destination=b.ksc.id,
        )

    def test_measures_of_effectiveness(self):
        sim = FullSimulator(self.builder.build())
        sim.simulate()
        self.assertEqual(sim.errors, [])
        self.assertEqual(sim.time, 13)
        self.assertEqual(
            final_locations(sim),
            {"Lander": "KSC", "A": "KSC", "B": "KSC", "Science": "LSP", "Power": "LSP"},
        )
        # two crew members spend 7 days at the lunar surface
        self.assertEqual(sim.total_crew_surface_days, 14)
        # with 500 kg of exploration and infrastructure items
        self.assertEqual(sim.total_exploration_capability, 14 * 500)
        self.assertEqual(sim.total_exploration_mass_delivered, 500)
        self.assertEqual(sim.total_launch_mass, 4700)
        self.assertEqual(sim.total_up_mass_capacity_utilization, 4700 / 10000)
        self.assertEqual(sim.total_down_mass_capacity_utilization, 4200 / 5000)
        self.assertEqual(sim.total_crew_time, 2 * 13 * 24)
        self.assertEqual(sim.get_total_crew_time(CREW_TIME_EXPLORATION), 13 * 24)
        self.assertEqual(sim.get_total_crew_time(CREW_TIME_UNAVAILABLE), 13 * 24)
        self.assertAlmostEqual(
            sim.total_relative_exploration_capability, (7000 / 2594) / (4700 / 2930000)
        )

    def test_network_history(self):
        b = self.builder
        sim = FullSimulator(b.build())
        sim.simulate()
        self.assertEqual([n.time for n in sim.network_history], [0, 0, 3, 10, 13])
        initial, launched, landed, departed, returned = sim.network_history
        self.assertEqual(initial.get_elements(b.ksc.id), [])
        self.assertEqual(launched.get_total_mass(b.ksc_lsp.id), 4700)
        lander = launched.get_elements(b.ksc_lsp.id)[0]
        self.assertEqual(lander.name, "Lander")
        self.assertEqual(lander.type, "Element Carrier")
        self.assertEqual(lander.crew_size, 2)
        self.assertEqual(lander.cargo_mass, 500)
        self.assertEqual(
            [e.name for e in lander.contents], ["A", "B", "Power", "Science"]
        )
        self.assertEqual(
            [e.name for e in landed.get_elements(b.lsp.id)],
            ["Lander", "Power", "Science"],
        )
        self.assertEqual(
            [e.name for e in departed.get_elements(b.lsp_ksc.id)], ["Lander"]
        )
        self.assertEqual(returned.get_total_mass(b.ksc.id), 4200)

    def test_simulation_is_repeatable_and_does_not_modify_scenario(self):
        scenario = self.builder.build()
        before = scenario.model_dump_json()
        sim = FullSimulator(scenario)
        sim.simulate()
        first = (sim.time, sim.total_launch_mass, len(sim.network_history))
        first_state = sim.state
        sim.simulate()
        self.assertEqual(
            first, (sim.time, sim.total_launch_mass, len(sim.network_history))
        )
        self.assertIsNot(sim.state, first_state)
        self.assertEqual(scenario.model_dump_json(), before)

    def test_errors_do_not_stop_simulation(self):
        b = self.builder
        b.missions[0].events.insert(
            3, b.move([self.science], b.leo, b.leo, days=1)  # not located at LEO
        )
        sim = FullSimulator(b.build())
        sim.simulate()
        self.assertEqual(len(sim.spatial_errors), 1)
        self.assertEqual(sim.spatial_errors[0].time, 1)
        self.assertEqual(sim.spatial_errors[0].event.name, "Move")
        self.assertEqual(final_locations(sim)["Lander"], "KSC")


class TestPreSimulator(unittest.TestCase):
    def setUp(self):
        self.builder = b = ScenarioBuilder()
        self.lander = b.carrier("Lander", mass=4000, max_cargo_mass=1000)
        self.cargo = b.element("Cargo", mass=600)
        b.mission(
            [
                b.create([self.lander], b.ksc),
                b.create([self.cargo], self.lander, location=b.ksc, priority=2),
                b.flight([self.lander], b.ksc_lsp, days=1, priority=2),
            ]
        )

    def _location(self, simulator):
        return simulator.state.get_element(self.lander.id).location.name

    def test_simulate_to_time(self):
        sim = PreSimulator(self.builder.build())
        sim.simulate(0.5)
        self.assertEqual(sim.time, 0.5)
        self.assertEqual(self._location(sim), "KSC")
        sim.simulate(2)
        self.assertEqual(self._location(sim), "KSC-LSP")
        sim.simulate()
        self.assertEqual(sim.time, 4)
        self.assertEqual(self._location(sim), "LSP")

    def test_simulate_to_priority(self):
        sim = PreSimulator(self.builder.build())
        sim.simulate(1, priority=2)
        self.assertEqual(self._location(sim), "KSC")
        sim.simulate(1, priority=3)
        self.assertEqual(self._location(sim), "KSC-LSP")

    def test_continue_without_reset(self):
        sim = PreSimulator(self.builder.build())
        sim.simulate(0.5)
        state = sim.state
        sim.simulate(2, reset=False)
        self.assertIs(sim.state, state)
        self.assertEqual(self._location(sim), "KSC-LSP")

    def test_simulate_to_event(self):
        sim = PreSimulator(self.builder.build())
        sim.simulate(2)
        flight = sim.state.missions[0].events[2]
        sim.simulate_to_event(flight)
        self.assertEqual(sim.time, 1)
        self.assertEqual(self._location(sim), "KSC")

    def test_mission_capacity(self):
        sim = MiniSimulator(self.builder.build())
        sim.simulate()
        mission = sim.state.missions[0]
        self.assertEqual([c.name for c in mission.delivery_carriers], ["Lander"])
        self.assertEqual(mission.return_carriers, [])
        self.assertEqual(mission.raw_delivery_capacity, 10000)
        self.assertEqual(mission.remaining_delivery_capacity, 10000 - 600)
        self.assertEqual(mission.raw_return_capacity, 0)


class TestDemandSimulator(unittest.TestCase):
    """
    A habitat demands 5 spares per year (as a fraction of its mass) and its
    crew demands water at a constant rate.
    """

    def _build(self, **configuration):
        self.builder = b = ScenarioBuilder(**configuration)
        sparing = s.SparingByMassDemandModel(
            name="Sparing",
            unpressurized_spares_rate=0.05,
            pressurized_spares_rate=0.10,
            parts_list_enabled=True,
        )
        b.demand_models = [sparing]
        self.habitat = b.add(
            s.ElementCarrier(
                name="Habitat",
                mass=7300,
                max_cargo_mass=1000,
                max_crew=2,
                parts=[
                    s.Part(
                        resource=b.spare.id,
                        quantity=100,
                        mean_time_to_repair=timedelta(hours=2),
                        mass_to_repair=1,
                    )
                ],
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
            s.InstElementCarrier,
        )
        self.crew = b.crew()
        self.wreck = b.add(
            s.Element(
                name="Wreck",
                mass=100,
                class_of_supply=8,
                parts=[s.Part(resource=b.spare.id, quantity=3)],
                states=[s.State(name="Decommissioned", type="Decommissioned")],
                current_state_index=0,
            ),
            s.InstElement,
        )
        b.mission(
            [
                b.create([self.habitat, self.wreck], b.lsp),
                b.create([self.crew], self.habitat, location=b.lsp, priority=2),
                # demands are generated whenever time advances to an event
                s.ReconfigureElements(
                    name="Reconfigure",
                    priority=1,
                    mission_time=timedelta(days=146),
                    location=b.lsp.id,
                    elements=[self.habitat.id],
                    state_type="Active",
                ),
            ],
            name="Crewed",
            origin=b.lsp.id,
        )
        b.mission([], name="Next", days=365, origin=b.lsp.id)
        return b.build()

    def _spares(self, simulator):
        spare = simulator.state.get_resource(self.builder.spare.id)
        return [
            (d.time, d.demands.get(spare).amount)
            for d in simulator.unsatisfied_demands
            if d.demands.get(spare) is not None
        ]

    def test_demand_history(self):
        sim = DemandSimulator(self._build(), demands_satisfied=False)
        sim.simulate()
        self.assertEqual(sim.spatial_errors, [])
        self.assertEqual(self._spares(sim), [(146, 2), (365, 3)])
        habitat = sim.state.get_element(self.habitat.id)
        crewed, following = sim.state.missions
        self.assertEqual(len(sim.get_demand_history(habitat)), 2)
        self.assertEqual(len(sim.get_demand_history(habitat.location)), 2)
        self.assertEqual(len(sim.get_demand_history(crewed)), 2)
        self.assertEqual(len(sim.get_demand_history(following)), 0)
        demands = sim.get_demands(crewed, element=habitat)
        # 5 spares of 5 kg and generic spares for the remaining mass
        self.assertAlmostEqual(demands.total_mass, 25 + 0.05 * 6800 + 0.10 * 7300)
        maintenance = sim.get_demands(habitat, class_of_supply=s.ClassOfSupply.COS_4)
        self.assertAlmostEqual(maintenance.total_mass, demands.total_mass)
        self.assertEqual(len(sim.get_demands(crewed, mission_level=True)), 0)
        self.assertEqual(len(sim.get_demands(habitat, class_of_supply=2)), 0)

    def test_repairable_demands(self):
        scenario = self._build()
        sim = DemandSimulator(scenario, demands_satisfied=False)
        sim.simulate()
        items = sim.sorted_repair_items[0]
        self.assertEqual(
            [i.demand.amount for i in sim.unsorted_repair_items[0]], [2, 3]
        )
        self.assertEqual(sim.sorted_repair_items[1], [])
        self.assertEqual(items[0].unit_mean_repair_time, 2)
        self.assertEqual(items[0].unit_mass_to_repair, 1)
        self.assertEqual(items[0].repair_value, 2 / (5 - 1))
        self.assertEqual(items[1].mean_repair_time, 6)
        self.assertEqual(items[1].mass_to_repair, 3)

        full = FullSimulator(scenario, repaired_items={0: items})
        full.simulate()
        self.assertEqual(self._spares(full), [])
        self.assertEqual(
            [
                (r.time, r.amount, r.repair_time, r.repair_mass)
                for r in full.repaired_parts
            ],
            [(146, 2, 4, 2), (365, 3, 6, 3)],
        )
        self.assertEqual(full.get_total_crew_time(CREW_TIME_CORRECTIVE_MAINTENANCE), 10)
        self.assertEqual(
            full.get_total_crew_time(CREW_TIME_EXPLORATION), 365 * 24 * 0.5 - 10
        )
        # repaired parts are replaced by a demand for the mass to repair
        habitat = full.state.get_element(self.habitat.id)
        self.assertAlmostEqual(
            full.get_demands(habitat).total_mass, 5 + 0.05 * 6800 + 0.10 * 7300
        )
        # the repair items provided to the simulator are not modified
        self.assertEqual(
            [i.demand.amount for i in sim.unsorted_repair_items[0]], [2, 3]
        )
        # repairs can be disabled
        full = FullSimulator(scenario, repaired_items={0: items}, items_repaired=False)
        full.simulate()
        self.assertEqual(self._spares(full), [(146, 2), (365, 3)])

    def test_scavenging(self):
        sim = FullSimulator(self._build(scavenge_spares=True))
        sim.simulate()
        # 3 spares are scavenged from the decommissioned element
        self.assertEqual(
            [(p.time, p.amount) for p in sim.scavenged_parts], [(146, 2), (365, 1)]
        )
        self.assertEqual(sim.scavenged_parts[0].element.name, "Wreck")
        self.assertEqual(self._spares(sim), [(365, 2)])
        wreck = sim.state.get_element(self.wreck.id)
        self.assertEqual(wreck.parts[0].quantity, 0)
        self.assertEqual(wreck.get_total_mass(s.ClassOfSupply.COS_4), 0)
        self.assertEqual(wreck.get_total_mass(s.ClassOfSupply.COS_8), 100)
        # without scavenging the parts remain in the decommissioned element
        sim = FullSimulator(self._build())
        sim.simulate()
        self.assertEqual(sim.scavenged_parts, [])
        self.assertEqual(self._spares(sim), [(146, 2), (365, 3)])

    def test_item_discretization(self):
        # fractional demands for items are accumulated to whole units
        for discretization in ("Element", "Location", "Scenario"):
            scenario = self._build(
                item_discretization=discretization, item_aggregation=1
            )
            scenario.mission_list[0].events[2].mission_time = timedelta(days=109.5)
            sim = DemandSimulator(scenario, demands_satisfied=False)
            sim.simulate()
            # 1.5 spares are demanded after 109.5 days and 3.5 spares thereafter
            self.assertEqual(self._spares(sim), [(109.5, 1), (365, 4)], discretization)
        scenario = self._build()
        scenario.mission_list[0].events[2].mission_time = timedelta(days=109.5)
        sim = DemandSimulator(scenario, demands_satisfied=False)
        sim.simulate()
        self.assertEqual(self._spares(sim), [(109.5, 1.5), (365, 3.5)])

    def test_aggregated_demands(self):
        b = ScenarioBuilder()
        water = s.RatedDemandModel(
            name="Water", demands=[s.ResourceAmountRate(resource=b.water.id, rate=2)]
        )
        b.demand_models = [water]
        lander = b.carrier("Lander", mass=4000, max_cargo_mass=1000)
        crew = b.add(
            s.HumanAgent(
                name="Crew",
                mass=100,
                active_time_fraction=0.5,
                states=[
                    s.State(
                        name="Active",
                        type="Active",
                        demand_models=[
                            s.InstRatedDemandModel(name="Water", template_id=water.id)
                        ],
                    )
                ],
                current_state_index=0,
            ),
            s.InstHumanAgent,
        )
        b.mission(
            [
                b.create([lander], b.ksc),
                b.create([crew], lander, location=b.ksc, priority=2),
                b.flight([lander], b.ksc_lsp, days=1, priority=3),
                b.flight([lander], b.lsp_ksc, days=10),
            ],
            return_origin=b.lsp.id,
            return_destination=b.ksc.id,
        )
        sim = DemandSimulator(b.build(), demands_satisfied=False)
        sim.simulate()
        self.assertEqual(sim.unassigned_demands, [])
        self.assertEqual(
            [
                (str(e.origin), str(e.destination), e.start_time, e.end_time)
                for e in sim.supply_edges
            ],
            [("LSP", "KSC", 10, 13), ("KSC", "LSP", 1, 4)],
        )
        self.assertEqual(
            [(str(p.node), p.time) for p in sim.supply_points],
            [("KSC", 13), ("LSP", 4)],
        )
        outbound = sim.supply_edges[1]
        self.assertEqual(outbound.max_cargo_mass, 10000)
        self.assertEqual(outbound.net_cargo_mass, 10000 - 4100)
        self.assertEqual([c.name for c in outbound.all_carriers], ["Lander"])

        analysis = AggregatedDemandsAnalysis.create(sim)
        # water is demanded in transit (3 days each way) and at the surface (6 days)
        self.assertEqual(
            [
                (n.location.name, n.time, n.total_consumption_mass)
                for n in analysis.nodes
            ],
            [("KSC", 13, 0), ("LSP", 4, 12)],
        )
        self.assertEqual(
            [(e.location.name, e.total_consumption_mass) for e in analysis.edges],
            [("LSP-KSC", 6), ("KSC-LSP", 6)],
        )
        resource = analysis.nodes[1].consumption[0]
        self.assertEqual(resource.resource.name, "Water")
        self.assertEqual(resource.resource.type, "Continuous")
        self.assertEqual(resource.amount, 12)
        data = analysis.model_dump(by_alias=True, mode="json")
        self.assertEqual(data["edges"][1]["maxCargoMass"], 10000)
        self.assertEqual(data["nodes"][1]["totalConsumptionMass"], 12)

        raw = RawDemandsAnalysis.create(sim)
        # the demand before launch at the surface of Earth is not aggregated
        self.assertEqual(
            [
                (d.time, d.location.name, d.element.name, d.total_consumption_mass)
                for d in raw.demands
            ],
            [
                (1, "KSC", "Crew", 2),
                (4, "KSC-LSP", "Crew", 6),
                (10, "LSP", "Crew", 12),
                (13, "LSP-KSC", "Crew", 6),
            ],
        )

    def test_demands_satisfied_by_available_resources(self):
        b = ScenarioBuilder()
        tank = b.container(
            "Tank",
            max_cargo_mass=20,
            contents=[s.ResourceAmount(resource=b.water.id, amount=15)],
        )
        consumer = b.element("Consumer")
        b.mission(
            [
                b.create([tank, consumer], b.lsp),
                *[
                    s.ConsumeResources(
                        name="Consume",
                        priority=1,
                        mission_time=timedelta(days=day),
                        location=b.lsp.id,
                        source=consumer.id,
                        resources=[s.ResourceAmount(resource=b.water.id, amount=10)],
                    )
                    for day in (1, 2)
                ],
            ],
            origin=b.lsp.id,
        )
        sim = DemandSimulator(b.build())
        sim.simulate()
        water = sim.state.get_resource(b.water.id)
        self.assertEqual(sim.state.get_element(tank.id).get_amount(water), 0)
        self.assertEqual(
            [(d.time, d.demands.get(water).amount) for d in sim.unsatisfied_demands],
            [(2, 5)],
        )
        self.assertIsInstance(sim.unsatisfied_demands[0].event, DemandEvent)


class TestQuickStartScenarios(unittest.TestCase):
    def test_quick_start_1(self):
        for path in (
            "quick_start/completed_quick_start_1_w_db.json",
            "quick_start/completed_quick_start_1_wo_db.json",
        ):
            sim = FullSimulator(load_scenario(path))
            sim.simulate()
            self.assertEqual(sim.errors, [], path)
            self.assertEqual(sim.warnings, [], path)
            self.assertEqual(sim.time, 19)
            locations = final_locations(sim)
            # the crew returns with samples and all other stages are expended
            self.assertEqual(
                locations,
                {
                    "Lunar | Orion CM": "PAC",
                    "Lunar | Crew Member A": "PAC",
                    "Lunar | Crew Member B": "PAC",
                    "Lunar | Crew Member C": "PAC",
                    "Lunar | Crew Member D": "PAC",
                    "Lunar | Lunar Surface Samples": "PAC",
                    "Lunar | Altair AM": "LLPO",
                    "Lunar | Altair DM": "LSP",
                    "Lunar | Notional Cargo": "LSP",
                },
            )
            mission = sim.state.missions[0]
            self.assertEqual(mission.crew_size, 4)
            self.assertEqual(mission.duration, 19)
            self.assertEqual(mission.transit_duration, 7.5)
            self.assertEqual(mission.destination_duration, 7)
            self.assertEqual(mission.number_eva, 5)
            self.assertEqual(sim.total_crew_surface_days, 4 * 7)
            self.assertEqual(sim.total_exploration_mass_delivered, 500)
            self.assertEqual(sim.total_exploration_capability, 4 * 7 * 500)
            # values of the reference implementation: orbital maneuvering
            # system (OMS) and reaction control system (RCS) burns consume
            # fuel from separate (Altair DM) or shared (Orion SM, Altair AM)
            # fuel tanks
            self.assertEqual(sim.total_launch_mass, 4559400)
            self.assertAlmostEqual(
                sim.total_relative_exploration_capability, 3.468310649296501
            )
            elements = {
                e.name: e
                for registrar in (
                    sim.state.network.registrar,
                    sim.state.network.removed_registrar,
                )
                for e in registrar.values()
            }
            self.assertEqual(
                {
                    name: [t.amount for t in elements[f"Lunar | {name}"].fuel_tanks]
                    for name in ("Altair DM", "Altair AM", "Orion SM", "Orion CM")
                },
                {
                    "Altair DM": [573.73, 262.27],
                    "Altair AM": [39.49],
                    "Orion SM": [3117.07],
                    "Orion CM": [160.32],
                },
            )

    def test_quick_start_2(self):
        scenario = load_scenario("quick_start/completed_quick_start_2_w_db.json")
        sim = DemandSimulator(scenario, demands_satisfied=False)
        sim.simulate()
        self.assertEqual(sim.spatial_errors, [])
        self.assertEqual(sim.warnings, [])
        self.assertEqual(sim.unassigned_demands, [])
        self.assertEqual(sim.time, 393)
        self.assertEqual(
            [(m.duration, m.crew_size, m.eva_crew_time) for m in sim.state.missions],
            [(153, 0, 0), (91, 4, 80), (122, 0, 0), (27, 4, 160)],
        )
        # crew consumables for 4 crew members over 7 days with 80 hours of EVA
        crew_days, eva = 4 * 7, 80
        expected = (
            crew_days * 3.6 * (1 - 0.42)
            + eva * 0.6875
            + crew_days * (0.05556 + 0.76389 + 1.61667)
            + crew_days * (3.85714 + 2.21429)
            + eva * 0.07875
            + crew_days * 0.27778
            + 4 * 1.8
            + crew_days * 2.3 / 4
            + 4 * (10 + 5 + 107 + 0.1 + 5)
            + eva * 0.3625
            + 20
            + 25
            + 20
            + crew_days * (0.05 + 0.05)
        )
        mission = sim.state.missions[1]
        demands = sim.get_demands(mission, mission_level=True)
        self.assertAlmostEqual(demands.total_mass, expected, delta=0.1)
        analysis = AggregatedDemandsAnalysis.create(sim)
        node = next(n for n in analysis.nodes if n.time == 160.5)
        self.assertEqual(node.location.name, "LSP")
        self.assertAlmostEqual(node.total_consumption_mass, expected, delta=0.1)

    def test_artemis_campaign(self):
        sim = FullSimulator(load_scenario("artemis/artemis_campaign.json"))
        sim.simulate()
        self.assertEqual(sim.errors, [])
        self.assertEqual(
            [w.message for w in sim.warnings],
            ["No events defined.", "No events defined."],
        )
        self.assertEqual(final_locations(sim)["Artemis 3 | Orion CM"], "PAC")

    def test_artemis_add_campaign(self):
        sim = FullSimulator(load_scenario("artemis/artemis_add_campaign.json"))
        sim.simulate()
        self.assertEqual(sim.spatial_errors, [])
        self.assertEqual(sim.warnings, [])
        locations = final_locations(sim)
        for mission in ("Artemis II", "Artemis III", "Artemis IV", "Artemis V"):
            self.assertEqual(locations[f"{mission} | Orion CM"], "PAC")
            self.assertEqual(locations[f"{mission} | Crew Member A"], "PAC")
        self.assertEqual(locations["Gateway | HALO"], "NRHO")
        self.assertEqual(locations["Artemis IV | I-Hab"], "NRHO")
        # the samples collected at the lunar south pole return to Earth
        self.assertEqual(locations["Artemis III | Lunar Samples"], "PAC")
        boiloff = [f for f in sim.propellant_flows if f.kind.value == "Boiloff"]
        self.assertTrue(any("Depot" in f.vehicle_name for f in boiloff))
        self.assertTrue(any("HLS" in f.vehicle_name for f in boiloff))
        # the crew consumables of the crewed missions are left to the manifest
        self.assertEqual(len(sim.unsatisfied_demands), 4)
        # surface power and mobility
        self.assertEqual(locations["Surface Cargo | LTV"], "LSP")
        self.assertEqual(locations["Surface Cargo | FSP"], "LSP")
        groups = {r.name for r in sim.power_records}
        self.assertIn("LSP Grid", groups)
        self.assertIn("Artemis III | HLS", groups)
        self.assertEqual(sum(r.deficit for r in sim.power_records), 0)
        grid = [r for r in sim.power_records if r.name == "LSP Grid"]
        # fission power and the solar arrays of the terrain vehicle
        self.assertAlmostEqual(max(r.generation for r in grid), 40 + 0.85 * 1.5)
        # the Artemis V crew drive the terrain vehicle to the second site
        site = next(n.id for n in sim.state.network.nodes if n.name == "LSP-2")
        visitors = {
            e.name
            for snapshot in sim.network_history
            for e in snapshot.get_elements(site)
        }
        self.assertIn("Artemis V | Crew Member A", visitors)
        self.assertIn("Surface Cargo | LTV", visitors)


if __name__ == "__main__":
    unittest.main()
