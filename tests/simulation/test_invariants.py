"""
Tests of invariants which every simulation must satisfy, checked for the
reference scenarios and for random scenarios (see :mod:`.generator`):

* time never decreases and no event executes after the scenario end
* each element is in exactly one container, consistent with its parent
* tanks, resource containers, and energy storage stay within their bounds
* every change to a vehicle tank is recorded (the propellant ledger closes)
* burns achieve the delta-v of the rocket equation
* transfers conserve resources (removed = delivered + lost)
* the recorded network history matches the simulation state
* the total mass of closed scenarios is constant
* simulations are deterministic and do not modify their scenario
* simulators agree on the errors and final locations of a scenario

A failure reports the seed of the random scenario, which reproduces it with
``random_scenario(seed)``.
"""

import logging
import math
import unittest
from collections import defaultdict

import pytest

from spacenet.simulation import (
    BurnEvent,
    DemandSimulator,
    FullSimulator,
    MiniSimulator,
    PropellantFlowKind,
    SimCarrier,
    SimCrewMember,
    SimResourceContainer,
    State,
    TransferEvent,
)
from spacenet.simulation.events import G0

from .generator import random_scenario
from .util import load_scenario

REFERENCE_SCENARIOS = (
    "quick_start/completed_quick_start_1_w_db.json",
    "quick_start/completed_quick_start_1_wo_db.json",
    "quick_start/completed_quick_start_2_w_db.json",
    "quick_start/completed_quick_start_3_wo_db.json",
    "artemis/artemis_campaign.json",
    "artemis/artemis_add_campaign.json",
)

#: Number of random scenarios checked in each run (more in slow tests).
SEEDS = range(40)
SLOW_SEEDS = range(40, 1000)

#: Absolute tolerance (units, kg, or kWh) of amounts.
TOLERANCE = 1e-6

#: Sign of the change to a tank of each kind of propellant flow.
FLOW_SIGNS = {
    PropellantFlowKind.ADDED: 1,
    PropellantFlowKind.TRANSFER_IN: 1,
    PropellantFlowKind.TRANSFER_OUT: -1,
    PropellantFlowKind.TRANSFER_LOSS: -1,
    PropellantFlowKind.BURNED: -1,
    PropellantFlowKind.BOILOFF: -1,
    PropellantFlowKind.CONSUMED: -1,
}


def close(a: float, b: float, relative: float = 1e-9) -> bool:
    """Compares amounts with a relative and an absolute tolerance."""
    return math.isclose(a, b, rel_tol=relative, abs_tol=TOLERANCE)


def all_elements(state: State):
    """Lists the elements of a state in the network or removed."""
    network = state.network
    return [*network.registrar.values(), *network.removed_registrar.values()]


class CheckedSimulator(FullSimulator):
    """
    Full simulator which checks the invariants of the simulation state after
    every event and records the information to check others afterwards.
    """

    def initialize_simulation(self):
        #: Descriptions of invariants violated during the simulation.
        self.violations = []
        #: Times of the executed events.
        self.event_times = []
        #: Executed burn and transfer events.
        self.burn_events = []
        self.transfer_events = []
        #: Total mass (kg) of the top-level contents of each location at each
        #: recorded time step.
        self.live_frames = []
        #: Total amount of each resource (by name) after creation.
        self.resource_totals = []
        super().initialize_simulation()

    def _violate(self, message: str):
        self.violations.append(f"t={self.time:g} ({self.event}): {message}")

    def _next_event(self):
        previous = self.time
        super()._next_event()
        if self.time < previous:
            self._violate(f"time decreased from {previous:g}")
        if self.end_time is not None and self.time > self.end_time:
            self._violate("event after the scenario end")
        self.event_times.append(self.time)

    def _execute_event(self):
        super()._execute_event()
        if isinstance(self.event, BurnEvent):
            self.burn_events.append(self.event)
        if isinstance(self.event, TransferEvent):
            self.transfer_events.append(self.event)
        self.check_state()

    def _record_network(self):
        super()._record_network()
        self.live_frames.append(
            (
                self.time,
                {
                    location.id: sum(e.total_mass for e in location.contents)
                    for location in self.state.network.locations
                },
            )
        )

    def check_state(self):
        """Checks the invariants of the current simulation state."""
        network = self.state.network
        seen = {}
        totals = defaultdict(float)

        def visit(container, element):
            if element.id in seen:
                self._violate(f"{element} is in {seen[element.id]} and {container}")
                return
            seen[element.id] = container
            if element.container is not container:
                self._violate(
                    f"{element} has parent {element.container}, not {container}"
                )
            if network.registrar.get(element.id) is not element:
                self._violate(f"{element} is in the network but not registered")
            self.check_element(element, totals)
            for child in getattr(element, "contents", ()):
                if not isinstance(element, SimResourceContainer):
                    visit(element, child)

        for location in network.locations:
            for element in location.contents:
                visit(location, element)
        for element_id, element in network.registrar.items():
            if element_id not in seen:
                self._violate(f"{element} is registered but not in the network")
        # elements are created at the start of closed scenarios
        if self.time > 0:
            self.resource_totals.append((self.time, dict(totals)))

    def check_element(self, element, totals):
        """Checks the bounds of the tanks, contents, and energy of an element."""
        precision = self.settings.demand_precision
        for tank in getattr(element, "fuel_tanks", None) or []:
            if tank.amount < -TOLERANCE or tank.amount > tank.max_amount + precision:
                self._violate(f"{tank} holds {tank.amount} of {tank.max_amount}")
            if tank.resource is not None:
                totals[tank.resource.name] += tank.amount
        if isinstance(element, SimResourceContainer):
            for resource, amount in element.contents.items():
                if amount < -TOLERANCE:
                    self._violate(f"{element} holds {amount} of {resource}")
                totals[resource.name] += amount
        capacity = getattr(element, "energy_capacity", 0.0)
        if element.energy < -TOLERANCE or element.energy > capacity + TOLERANCE:
            self._violate(f"{element} stores {element.energy} of {capacity} kWh")
        if isinstance(element, SimCarrier):
            if element.crew_size > element.max_crew_size and not self._initial(element):
                self._violate(f"{element} has {element.crew_size} crew")

    def _initial(self, element) -> bool:
        """True, if an element is in its initial (unchecked) configuration."""
        return element.created_time is None


class InvariantChecks:
    """Checks of the invariants of executed simulations."""

    # pylint: disable=no-member

    def simulate(self, scenario):
        """Simulates a scenario with invariant checks."""
        simulator = CheckedSimulator(scenario)
        simulator.simulate()
        self.assertEqual(simulator.violations, [])
        return simulator

    def check_simulation(self, scenario):
        """Checks the invariants of a scenario."""
        before = scenario.model_dump_json()
        simulator = self.simulate(scenario)
        self.check_times(simulator)
        self.check_propellant_ledger(scenario, simulator)
        self.check_burns(simulator)
        self.check_transfers(simulator)
        self.check_records(simulator)
        self.check_history(simulator)
        self.check_determinism(scenario, simulator)
        self.check_simulators_agree(scenario, simulator)
        self.assertEqual(scenario.model_dump_json(), before, "scenario modified")
        return simulator

    def check_times(self, simulator):
        """Checks that time never decreases and ends at the scenario end."""
        self.assertEqual(simulator.event_times, sorted(simulator.event_times))
        if simulator.end_time is not None:
            self.assertEqual(simulator.time, simulator.end_time)
        times = [frame.time for frame in simulator.network_history]
        self.assertEqual(times, sorted(times))

    def check_propellant_ledger(self, scenario, simulator):
        """
        Checks that the final contents of each vehicle tank equal its initial
        contents plus the recorded changes.
        """
        initial = State(scenario)
        flows = defaultdict(list)
        for flow in simulator.propellant_flows:
            flows[(flow.vehicle_id, flow.tank_key)].append(flow)
        initial_tanks = {
            (e.id, t.key): t
            for e in initial.elements.values()
            for t in getattr(e, "fuel_tanks", None) or []
        }
        for element in all_elements(simulator.state):
            for tank in getattr(element, "fuel_tanks", None) or []:
                key = (element.id, tank.key)
                # tank amounts are rounded to the demand precision; flows are not
                final = tank._amount  # pylint: disable=protected-access
                amount = initial_tanks[key]._amount  # pylint: disable=protected-access
                for index, flow in enumerate(flows.get(key, [])):
                    if flow.kind == PropellantFlowKind.LOADED:
                        self.assertEqual(index, 0, f"{tank} loaded twice")
                        self.assertTrue(close(flow.amount, amount), f"{tank} loaded")
                        continue
                    self.assertGreaterEqual(flow.max_amount, 0)
                    amount += FLOW_SIGNS[flow.kind] * flow.amount
                self.assertTrue(
                    close(amount, final, 1e-7),
                    f"{element} {tank.key}: ledger {amount} != tank {final}",
                )
                if flows.get(key):
                    self.assertTrue(
                        close(flows[key][-1].amount_after, final),
                        f"{element} {tank.key}: last flow != tank {final}",
                    )

    def check_burns(self, simulator):
        """Checks that burns achieve the delta-v of the rocket equation."""
        for event in simulator.burn_events:
            for step in event.steps:
                if step.action != "Burn" or step.propellant_mass_used <= 0:
                    continue
                vehicle = simulator.state.get_element(step.element_id)
                system = vehicle.get_propulsion_system(event.burn.propulsion_type)
                expected = (
                    system.isp
                    * G0
                    * math.log(
                        step.stack_mass / (step.stack_mass - step.propellant_mass_used)
                    )
                )
                self.assertTrue(
                    close(step.delta_v_achieved, expected, 1e-6),
                    f"{event} {step}: achieved {step.delta_v_achieved} != {expected}",
                )
                self.assertLessEqual(step.delta_v_achieved, event.burn.delta_v + 1e-6)

    def check_transfers(self, simulator):
        """Checks that transfers conserve the removed resources."""
        for event in simulator.transfer_events:
            for step in event.results:
                self.assertGreaterEqual(step.removed, -TOLERANCE)
                self.assertTrue(close(step.removed, step.delivered + step.lost))
                self.assertTrue(close(step.lost, step.removed * event.loss_fraction))

    def check_records(self, simulator):
        """Checks the bounds and ordering of interval records."""
        for records in (
            simulator.power_records,
            simulator.isru_records,
            simulator.failure_records,
            simulator.cost_records,
            simulator.propellant_flows,
        ):
            times = [r.time for r in records]
            self.assertEqual(times, sorted(times))
        for record in simulator.power_records:
            self.assertGreaterEqual(record.duration, 0)
            self.assertGreaterEqual(record.energy, -TOLERANCE)
            self.assertLessEqual(record.energy, record.capacity + TOLERANCE)
            self.assertGreaterEqual(record.deficit, 0)
            if record.deficit > TOLERANCE:
                self.assertTrue(close(record.energy, 0))
        for record in simulator.isru_records:
            self.assertTrue(0 <= record.rate <= 1 + 1e-9)
        for record in simulator.failure_records:
            self.assertGreaterEqual(record.failures, 0)
            self.assertGreaterEqual(record.duration, 0)
        for flow in simulator.propellant_flows:
            if flow.kind != PropellantFlowKind.CONSUMED:
                self.assertGreaterEqual(flow.amount, 0, flow)

    def check_history(self, simulator):
        """Checks that the recorded history composes the simulated states."""
        history = list(simulator.network_history)
        self.assertEqual(len(history), len(simulator.live_frames))
        for snapshot, (time, masses) in zip(history, simulator.live_frames):
            self.assertEqual(snapshot.time, time)
            for location_id, mass in masses.items():
                self.assertTrue(
                    close(snapshot.get_total_mass(location_id), mass, 1e-9),
                    f"history at {time}",
                )

    def check_determinism(self, scenario, simulator):
        """Checks that simulations of a scenario (and its copy) are identical."""
        expected = signature(simulator)
        again = FullSimulator(scenario)
        again.simulate()
        self.assertEqual(signature(again), expected)
        copy = type(scenario).model_validate_json(scenario.model_dump_json())
        copied = FullSimulator(copy)
        copied.simulate()
        self.assertEqual(signature(copied), expected)
        # a simulator can be executed again
        simulator.simulate()
        self.assertEqual(signature(simulator), expected)

    def check_simulators_agree(self, scenario, simulator):
        """Checks that simulators agree on errors and final locations."""
        if scenario.manifest is not None and scenario.manifest.loads:
            return  # only the full simulator loads the manifest
        for cls in (MiniSimulator, DemandSimulator):
            other = cls(scenario)
            other.simulate()
            self.assertEqual(other.time, simulator.time, cls.__name__)
            self.assertEqual(
                [(e.time, e.message) for e in other.spatial_errors],
                [(e.time, e.message) for e in simulator.spatial_errors],
                cls.__name__,
            )
            self.assertEqual(locations(other), locations(simulator), cls.__name__)


def locations(simulator) -> dict:
    """Gets the final location (name) of each element of a simulation."""
    return {
        e.id: None if e.location is None else e.location.name
        for e in all_elements(simulator.state)
    }


def signature(simulator) -> tuple:
    """Summarizes the results of a full simulation."""
    return (
        simulator.time,
        tuple((e.time, e.message) for e in simulator.spatial_errors),
        tuple((w.time, w.message) for w in simulator.warnings),
        tuple(
            (d.time, round(d.demands.total_mass, 9))
            for d in simulator.unsatisfied_demands
        ),
        tuple(
            (f.time, f.vehicle_name, f.tank_key, f.kind, round(f.amount, 9))
            for f in simulator.propellant_flows
        ),
        tuple((r.time, r.key, round(r.energy, 9)) for r in simulator.power_records),
        tuple((r.time, r.part_name, r.failures) for r in simulator.failure_records),
        tuple(sorted((str(k), v or "") for k, v in locations(simulator).items())),
        round(simulator.total_launch_mass, 6),
        round(simulator.total_crew_time, 6),
    )


class TestReferenceScenarios(InvariantChecks, unittest.TestCase):
    def test_reference_scenarios(self):
        for path in REFERENCE_SCENARIOS:
            with self.subTest(path):
                self.check_simulation(load_scenario(path))


class TestRandomScenarios(InvariantChecks, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # events of random scenarios often fail by design
        logging.disable(logging.WARNING)

    @classmethod
    def tearDownClass(cls):
        logging.disable(logging.NOTSET)

    def check_seeds(self, seeds, closed=False):
        """Checks the invariants of the random scenarios of a range of seeds."""
        for seed in seeds:
            with self.subTest(seed=seed, closed=closed):
                simulator = self.check_simulation(random_scenario(seed, closed))
                if closed:
                    self.check_closed(simulator)

    def check_closed(self, simulator):
        """Checks that the total resources and mass of a closed scenario are constant."""
        totals = simulator.resource_totals
        for time, amounts in totals:
            for name, amount in amounts.items():
                self.assertTrue(
                    close(amount, totals[0][1].get(name, 0.0), 1e-9),
                    f"{name} at {time}: {amount} != {totals[0][1].get(name)}",
                )
        frames = [sum(m.values()) for t, m in simulator.live_frames if t > 0]
        for mass in frames:
            self.assertTrue(close(mass, frames[0], 1e-9), f"{mass} != {frames[0]}")

    def test_random_scenarios(self):
        self.check_seeds(SEEDS)

    def test_closed_scenarios(self):
        self.check_seeds(SEEDS, closed=True)

    @pytest.mark.slow
    def test_many_random_scenarios(self):
        self.check_seeds(SLOW_SEEDS)
        self.check_seeds(SLOW_SEEDS, closed=True)


class TestGenerator(unittest.TestCase):
    def test_scenarios_are_reproducible(self):
        # identifiers differ, but the generated scenarios are otherwise equal
        first, second = random_scenario(7), random_scenario(7)
        self.assertEqual(first.end_date, second.end_date)
        self.assertEqual(
            [(t.name, t.mass) for t in first.element_templates],
            [(t.name, t.mass) for t in second.element_templates],
        )
        self.assertEqual(
            [[e.type for e in m.events] for m in first.mission_list],
            [[e.type for e in m.events] for m in second.mission_list],
        )

    def test_scenarios_exercise_events(self):
        types = set()
        failures = successes = 0
        logging.disable(logging.WARNING)
        try:
            for seed in SEEDS:
                scenario = random_scenario(seed)
                types.update(e.type for m in scenario.mission_list for e in m.events)
                simulator = FullSimulator(scenario)
                simulator.simulate()
                failures += len(simulator.spatial_errors)
                successes += sum(len(m.events) for m in scenario.mission_list)
        finally:
            logging.disable(logging.NOTSET)
        self.assertGreaterEqual(len(types), 11)
        # most events succeed
        self.assertLess(failures, successes / 4)


if __name__ == "__main__":
    unittest.main()
