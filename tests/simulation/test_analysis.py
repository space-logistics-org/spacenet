"""
Tests of the analyses which report simulation results as object schemas.
"""

import json
import unittest
from datetime import timedelta

from spacenet import schemas as s
from spacenet.simulation import (
    DemandsAnalysis,
    EventEvaluation,
    FullSimulator,
    MiniSimulator,
    MissionsAnalysis,
    ScenarioError,
    SimulationAnalysis,
    State,
    StateAnalysis,
)
from spacenet.simulation.analysis import (
    export_aggregated_demands,
    export_raw_demands,
)

from .util import ScenarioBuilder, load_scenario

SCENARIOS = (
    "quick_start/completed_quick_start_1_w_db.json",
    "quick_start/completed_quick_start_1_wo_db.json",
    "quick_start/completed_quick_start_2_w_db.json",
    "quick_start/completed_quick_start_3_wo_db.json",
    "artemis/artemis_campaign.json",
    "artemis/artemis_add_campaign.json",
)


def build_flight():
    """Builds a scenario which flies a carrier with one crew member to LSP."""
    builder = ScenarioBuilder()
    carrier = builder.carrier()
    crew = builder.crew()
    builder.mission(
        [
            builder.create([carrier], builder.ksc),
            builder.create([crew], carrier, location=builder.ksc, priority=2),
            builder.flight([carrier], builder.ksc_lsp, priority=3),
        ]
    )
    return builder, carrier, crew


def build_transport(fuel=9000):
    """Builds a scenario which launches a stage with a payload to LEO."""
    builder = ScenarioBuilder()
    stage = builder.vehicle(fuel=fuel)
    payload = builder.element("Payload", mass=500, class_of_supply=6)
    transport = s.SpaceTransport(
        name="Launch",
        priority=2,
        mission_time=timedelta(0),
        location=builder.ksc.id,
        edge=builder.ksc_leo.id,
        elements=[stage.id, payload.id],
        burn_stage_sequence=[
            s.BurnStageSequence(
                burn=builder.burn.id,
                actions=[
                    s.BurnStageItem(element=stage.id, type="Burn"),
                    s.BurnStageItem(element=stage.id, type="Stage"),
                ],
            )
        ],
    )
    builder.mission(
        [builder.create([stage, payload], builder.ksc), transport],
        destination=builder.leo.id,
    )
    return builder, stage, payload, transport


class TestEventSources(unittest.TestCase):
    def test_events_reference_their_mission_and_position(self):
        builder, _, _ = build_flight()
        state = State(builder.build())
        self.assertEqual(
            [e.source for e in state.missions[0].events], [(0, 0), (0, 1), (0, 2)]
        )

    def test_errors_of_derived_events_reference_the_scenario_event(self):
        builder, carrier, _ = build_flight()
        # the carrier is moved away before the arrival of the flight
        builder.missions[0].events.append(
            s.RemoveElements(
                name="Remove",
                priority=1,
                mission_time=timedelta(days=1),
                location=builder.ksc_lsp.id,
                elements=[carrier.id],
            )
        )
        simulator = MiniSimulator(builder.build())
        simulator.simulate()
        (error,) = simulator.spatial_errors
        self.assertEqual(error.event.source, (0, 2))
        self.assertIsNot(error.event, error.event.root)

    def test_scenario_errors_reference_the_event(self):
        builder, _, _ = build_flight()
        scenario = builder.build()
        scenario.mission_list[0].events[1].elements.append(builder.water.id)
        with self.assertRaises(ScenarioError) as context:
            State(scenario)
        self.assertEqual(context.exception.mission_index, 0)
        self.assertEqual(context.exception.event_index, 1)
        self.assertIsInstance(context.exception, ValueError)
        scenario = builder.build()
        scenario.mission_list[0].origin = builder.water.id
        with self.assertRaises(ScenarioError) as context:
            State(scenario)
        self.assertEqual(context.exception.mission_index, 0)
        self.assertIsNone(context.exception.event_index)


class TestMissionsAnalysis(unittest.TestCase):
    def test_summarizes_missions_and_events(self):
        builder, carrier, crew = build_flight()
        analysis = MissionsAnalysis.create(builder.build())
        self.assertEqual(analysis.issues, [])
        (mission,) = analysis.missions
        self.assertEqual(mission.crew_size, 1)
        self.assertEqual(mission.duration, 3)
        flight = mission.events[2]
        self.assertEqual(flight.type, "Flight Transport")
        self.assertEqual(flight.duration, 3)
        self.assertEqual(flight.origin, builder.ksc.id)
        self.assertEqual(flight.destination, builder.lsp.id)
        self.assertEqual(analysis.end_time, 3)
        history = {h.element.id: h for h in analysis.element_history}
        self.assertEqual(
            [
                (x.location, x.start_time, x.end_time)
                for x in history[carrier.id].segments
            ],
            [
                (builder.ksc.id, 0, 0),
                (builder.ksc_lsp.id, 0, 3),
                (builder.lsp.id, 3, 3),
            ],
        )
        self.assertEqual(len(history[crew.id].segments), 3)
        self.assertEqual(len(analysis.locations), 8)

    def test_errors_are_assigned_to_events(self):
        builder, _, _ = build_flight()
        del builder.missions[0].events[0]  # the carrier is never created
        analysis = MissionsAnalysis.create(builder.build())
        (mission,) = analysis.missions
        self.assertEqual(mission.error_count, 2)
        self.assertEqual([len(e.errors) for e in mission.events], [1, 1])
        self.assertEqual(
            [(i.kind, i.mission_index, i.event_index) for i in analysis.issues],
            [("spatial", 0, 0), ("spatial", 0, 1)],
        )

    def test_example_scenarios_have_no_errors(self):
        for path in SCENARIOS:
            analysis = MissionsAnalysis.create(load_scenario(path))
            self.assertEqual(
                [i for i in analysis.issues if i.kind != "warning"], [], path
            )
            json.loads(analysis.model_dump_json(by_alias=True))


class TestStateAnalysis(unittest.TestCase):
    def test_state_before_an_event(self):
        builder, carrier, crew = build_flight()
        scenario = builder.build()
        state = StateAnalysis.create(scenario, 0, 0, 3)
        locations = {l.name: l for l in state.locations}
        (element,) = locations["KSC"].elements
        self.assertEqual(element.id, carrier.id)
        self.assertTrue(element.is_carrier)
        self.assertEqual(element.max_cargo_mass, 5000)
        self.assertEqual(element.max_crew_size, 2)
        self.assertEqual([c.id for c in element.contents], [crew.id])
        self.assertTrue(element.contents[0].is_crew)
        self.assertEqual(locations["LSP"].elements, [])
        # in flight
        state = StateAnalysis.create(scenario, 0, 1, 1)
        locations = {l.name: l for l in state.locations}
        self.assertEqual(len(locations["KSC-LSP"].elements), 1)
        self.assertTrue(locations["KSC-LSP"].is_edge)

    def test_event_can_be_excluded(self):
        builder, _, _ = build_flight()
        scenario = builder.build()
        state = StateAnalysis.create(scenario, 0, 1, 1, exclude_event_index=2)
        locations = {l.name: l for l in state.locations}
        self.assertEqual(len(locations["KSC"].elements), 1)
        with self.assertRaises(ValueError):
            StateAnalysis.create(scenario, 1, 0, 1)
        with self.assertRaises(ValueError):
            StateAnalysis.create(scenario, 0, 0, 1, exclude_event_index=5)

    def test_vehicle_state_includes_fuel(self):
        builder, stage, _, _ = build_transport()
        state = StateAnalysis.create(builder.build(), 0, 0, 2)
        vehicle = next(e for e in state.locations[0].elements if e.id == stage.id)
        self.assertEqual(vehicle.fuel_amount, 9000)
        self.assertEqual(vehicle.max_fuel_amount, 9000)
        self.assertEqual(vehicle.isp, 300)
        self.assertEqual(vehicle.fuel_name, "Fuel")
        self.assertEqual(vehicle.mass_by_class_of_supply, {1: 9000.0})
        (tank,) = vehicle.fuel_tanks
        self.assertEqual(tank.label, "OMS Fuel")
        self.assertEqual(tank.amount, 9000)
        self.assertEqual(tank.propulsion, {"OMS": 300})

    def test_vehicle_state_includes_each_fuel_tank(self):
        builder = ScenarioBuilder()
        shared = builder.vehicle("Shared", fuel=9000, isp=300, rcs_isp=200)
        separate = builder.vehicle(
            "Separate", fuel=9000, isp=300, rcs_isp=200, rcs_fuel=50
        )
        rover = builder.rover()
        builder.mission([builder.create([shared, separate, rover], builder.ksc)])
        state = StateAnalysis.create(builder.build(), 0, 0, 2)
        elements = {e.id: e for e in state.locations[0].elements}
        (tank,) = elements[shared.id].fuel_tanks
        self.assertEqual(tank.label, "OMS/RCS Fuel")
        self.assertEqual(tank.propulsion, {"OMS": 300, "RCS": 200})
        oms, rcs = elements[separate.id].fuel_tanks
        self.assertEqual((oms.label, oms.amount), ("OMS Fuel", 9000))
        self.assertEqual((rcs.label, rcs.amount), ("RCS Fuel", 50))
        self.assertEqual(elements[separate.id].resources, {"Fuel": 9050})
        self.assertEqual(elements[separate.id].fuel_amount, 9000)
        (tank,) = elements[rover.id].fuel_tanks
        self.assertEqual((tank.label, tank.amount), ("Fuel", 100))


class TestEventEvaluation(unittest.TestCase):
    def test_space_transport_burns(self):
        builder, stage, _, transport = build_transport()
        scenario = builder.build()
        evaluation = EventEvaluation.create(scenario, 0, transport, 1)
        self.assertEqual(evaluation.issues, [])
        self.assertEqual(evaluation.duration, 0.25)
        self.assertEqual(evaluation.transport.destination, builder.leo.id)
        (burn,) = evaluation.burns
        self.assertTrue(burn.executed)
        self.assertEqual(burn.burn_id, builder.burn.id)
        self.assertEqual(burn.stack_mass, 10500)
        self.assertEqual(burn.delta_v_required, 1000)
        self.assertAlmostEqual(burn.delta_v_achieved, 1000)
        self.assertAlmostEqual(burn.delta_v_remaining, 0)
        self.assertEqual([x.action for x in burn.steps], ["Burn", "Stage"])
        self.assertEqual(burn.steps[0].element_id, stage.id)
        self.assertAlmostEqual(
            burn.steps[0].fuel_used + burn.steps[0].fuel_remaining, 9000
        )
        self.assertLess(burn.steps[1].stack_mass, 10500)
        # a following event starts at the destination on arrival
        self.assertEqual(evaluation.next.mission_time, 0.25)
        self.assertEqual(evaluation.next.location, builder.leo.id)
        self.assertEqual(evaluation.next.priority, 1)
        # the scenario is not modified
        self.assertEqual(len(scenario.mission_list[0].events), 2)

    def test_draft_without_burn_sequence_achieves_no_delta_v(self):
        builder, _, _, transport = build_transport()
        draft = transport.model_copy(update={"burn_stage_sequence": []})
        evaluation = EventEvaluation.create(builder.build(), 0, draft, 1)
        self.assertEqual(evaluation.burns[0].delta_v_remaining, 1000)
        self.assertEqual(evaluation.burns[0].delta_v_achieved, 0)
        self.assertEqual(evaluation.burns[0].steps, [])
        (issue,) = evaluation.issues
        self.assertIn("Insufficient delta-v", issue.message)
        self.assertEqual((issue.mission_index, issue.event_index), (0, 1))

    def test_insufficient_fuel(self):
        builder, _, _, transport = build_transport(fuel=100)
        evaluation = EventEvaluation.create(builder.build(), 0, transport, 1)
        burn = evaluation.burns[0]
        self.assertGreater(burn.delta_v_remaining, 0)
        self.assertAlmostEqual(burn.delta_v_achieved + burn.delta_v_remaining, 1000)
        self.assertEqual(burn.steps[0].fuel_remaining, 0)
        self.assertEqual(len(evaluation.issues), 1)

    def test_new_event_is_added_to_the_mission(self):
        builder, carrier, _ = build_flight()
        scenario = builder.build()
        flight = builder.flight([carrier], builder.lsp_ksc, days=5)
        evaluation = EventEvaluation.create(scenario, 0, flight)
        self.assertEqual(evaluation.issues, [])
        self.assertEqual(evaluation.transport.cargo_mass, 1100)
        self.assertEqual(evaluation.transport.max_cargo_mass, 5000)
        self.assertEqual(evaluation.transport.crew_size, 1)
        self.assertEqual(evaluation.transport.max_crew_size, 2)
        self.assertEqual(evaluation.next.mission_time, 8)

    def test_capacity_of_receiving_carrier(self):
        builder, carrier, _ = build_flight()
        cargo = builder.element("Cargo", mass=6000)
        scenario = builder.build()
        create = builder.create([cargo], carrier, location=builder.ksc, priority=2)
        evaluation = EventEvaluation.create(scenario, 0, create)
        self.assertEqual(len(evaluation.issues), 1)
        self.assertEqual(evaluation.container.id, carrier.id)
        self.assertEqual(evaluation.container.cargo_mass, 0)
        self.assertEqual(evaluation.next.priority, 3)
        self.assertEqual(evaluation.next.location, builder.ksc.id)

    def test_evaluates_all_events_of_example_scenarios(self):
        for path in SCENARIOS:
            scenario = load_scenario(path)
            for mission_index, mission in enumerate(scenario.mission_list):
                for event_index, event in enumerate(mission.events):
                    evaluation = EventEvaluation.create(
                        scenario, mission_index, event, event_index
                    )
                    self.assertEqual(evaluation.issues, [], f"{path} {event.name}")
                    for burn in evaluation.burns:
                        self.assertTrue(burn.executed)
                        self.assertAlmostEqual(burn.delta_v_remaining, 0, 5)


class TestDemandsAnalysis(unittest.TestCase):
    def test_quick_start_2(self):
        scenario = load_scenario("quick_start/completed_quick_start_2_w_db.json")
        simulator = DemandsAnalysis.simulate(scenario)
        analysis = DemandsAnalysis.create(simulator)
        self.assertEqual(len(analysis.raw.demands), 44)
        self.assertEqual(len(analysis.aggregated.nodes), 6)
        self.assertEqual(len(analysis.supply_edges), 6)
        self.assertEqual(len(analysis.supply_points), 6)
        self.assertEqual(sum(len(n.consumption) for n in analysis.aggregated.nodes), 30)
        total = sum(d.total_consumption_mass for d in analysis.raw.demands)
        self.assertAlmostEqual(analysis.total_mass, total)
        self.assertAlmostEqual(
            sum(p.demand_mass for p in analysis.supply_points)
            + analysis.unassigned_mass,
            total,
        )
        self.assertAlmostEqual(sum(x.total_mass for x in analysis.by_mission), total)
        self.assertAlmostEqual(sum(x.total_mass for x in analysis.by_location), total)
        for source in analysis.by_element + analysis.by_mission:
            self.assertAlmostEqual(
                sum(source.mass_by_class_of_supply.values()), source.total_mass
            )
            for series in source.series:
                masses = [p[1] for p in series.points]
                self.assertEqual(masses, sorted(masses))
                self.assertAlmostEqual(
                    masses[-1], source.mass_by_class_of_supply[series.class_of_supply]
                )
        moon = next(f for f in analysis.feasibility if f.location.name == "LSP")
        self.assertEqual(len(moon.points), 4)
        self.assertAlmostEqual(
            moon.points[-1].cumulative_demand_mass, analysis.total_mass
        )
        json.loads(analysis.model_dump_json(by_alias=True))
        self.assertEqual(len(export_raw_demands(simulator).splitlines()), 92)
        self.assertEqual(
            len(export_aggregated_demands(simulator, "\t").splitlines()), 31
        )

    def test_packing_demands_are_added(self):
        scenario = load_scenario("quick_start/completed_quick_start_2_w_db.json")
        base = DemandsAnalysis.create(DemandsAnalysis.simulate(scenario))
        packed = DemandsAnalysis.create(
            DemandsAnalysis.simulate(scenario, estimate_container_masses=True)
        )
        self.assertGreater(packed.total_mass, base.total_mass)


class TestSimulationAnalysis(unittest.TestCase):
    def test_example_scenarios(self):
        for path in SCENARIOS:
            scenario = load_scenario(path)
            simulator = FullSimulator(scenario)
            simulator.simulate()
            analysis = SimulationAnalysis.create(scenario)
            self.assertEqual(analysis.error_count, len(simulator.spatial_errors))
            self.assertEqual(
                analysis.unsatisfied_demand_count, len(simulator.unsatisfied_demands)
            )
            totals = analysis.totals
            self.assertEqual(totals.launch_mass, simulator.total_launch_mass)
            self.assertEqual(totals.crew_time, simulator.total_crew_time)
            self.assertEqual(
                totals.crew_surface_days, simulator.total_crew_surface_days
            )
            self.assertEqual(
                totals.exploration_capability, simulator.total_exploration_capability
            )
            self.assertAlmostEqual(
                sum(r.amount for r in analysis.measures.exploration_capability),
                simulator.total_exploration_capability,
            )
            self.assertEqual(
                len(analysis.network_history), len(simulator.network_history)
            )
            times = len(analysis.network_history)
            for history in analysis.location_history + analysis.element_history:
                for series in history.series:
                    self.assertEqual(len(series.points), times, path)
            json.loads(analysis.model_dump_json(by_alias=True))

    def test_mass_histories(self):
        builder, stage, payload, _ = build_transport()
        analysis = SimulationAnalysis.create(builder.build())
        self.assertEqual([s.time for s in analysis.network_history], [0, 0, 0.25])
        locations = {h.name: h for h in analysis.location_history}
        self.assertEqual(locations["KSC"].series, [])
        (in_transit,) = locations["KSC-LEO"].series
        self.assertEqual(in_transit.class_of_supply, 6)
        self.assertEqual(in_transit.points, [[0, 0], [0, 500], [0.25, 0]])
        (delivered,) = locations["LEO"].series
        self.assertEqual([p[1] for p in delivered.points], [0, 0, 500])
        # the stage is discarded at departure
        elements = {h.id: h for h in analysis.element_history}
        self.assertNotIn(stage.id, elements)
        (series,) = elements[payload.id].series
        self.assertEqual([p[1] for p in series.points], [0, 500, 500])
        leo = analysis.network_history[-1].locations[builder.leo.id]
        self.assertEqual([e.id for e in leo], [payload.id])
