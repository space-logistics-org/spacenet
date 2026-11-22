"""
Simulators which execute the events of a scenario as a discrete event simulation.
"""

# pylint: disable=too-many-lines

import heapq
import logging
import math
from collections import defaultdict
from typing import Dict, List, Optional, Tuple
from uuid import UUID

import numpy as np

from ..schemas import Body, ClassOfSupply, Scenario, StateType
from ..schemas.scenarios.scenario import PartFailureMode
from ..schemas.elements.power import PowerGenerationType
from ..schemas.scenarios.scenario import ItemDiscretizationType
from .elements import (
    ElementContainer,
    SimCarrier,
    SimCrewMember,
    SimElement,
    SimResourceContainer,
    SimResourceTank,
)
from .demand_models import SimISRUProcessModel
from .errors import SimDemand, SimError, SimSpatialError, SimWarning
from .events import (
    LAST_PRIORITY,
    DemandEvent,
    FlightTransportEvent,
    MissionEvent,
    SimEvent,
    SpaceTransportEvent,
    SurfaceTransportEvent,
    TransportEvent,
)
from .mission import SimMission
from .network import SimEdge, SimLocation, SimNode
from .records import (
    CREW_TIME_CORRECTIVE_MAINTENANCE,
    CREW_TIME_EXPLORATION,
    CREW_TIME_UNAVAILABLE,
    ElementSnapshot,
    LocationSnapshot,
    MoeCrewSurfaceDays,
    MoeCrewTime,
    MoeExplorationCapability,
    MoeExplorationMassDelivered,
    MoeLaunchMass,
    MoeMassCapacityUtilization,
    NetworkHistory,
    PropellantFlow,
    CostRecord,
    FailureRecord,
    ISRURecord,
    PowerRecord,
    PropellantFlowKind,
    SimRepair,
    SimScavenge,
)
from .resources import Demand, DemandSet, SimResource
from .settings import Settings
from .state import State
from .supply import RepairItem, SupplyEdge, SupplyPoint

logger = logging.getLogger(__name__)


class _ISRUPlan:
    """The planned operation of an ISRU process over an interval of time."""

    # pylint: disable=too-few-public-methods

    def __init__(self, element: SimElement, model: SimISRUProcessModel):
        self.element = element
        self.model = model
        #: Rate (fraction of the full rate) allowed by the constraints.
        self.rate = 1.0
        #: Constraint which limits the rate (None if unconstrained).
        self.limit: Optional[str] = None
        #: Resource which limits the rate (if limited by inputs or storage).
        self.resource: Optional[SimResource] = None


#: Exploration capability (kg-days) of the Apollo 17 mission.
APOLLO_17_EXPLORATION_CAPABILITY = 2594.0

#: Launch mass (kg) of the Apollo 17 mission.
APOLLO_17_LAUNCH_MASS = 2930000.0

#: Synodic day (days) of each body (the period of the day-night cycle).
SYNODIC_DAYS = {Body.MOON: 29.53, Body.MARS: 1.03, Body.EARTH: 1.0}


class Simulator:
    """
    Base class for a simulator that executes events following a discrete event
    simulation. Each simulation starts from a new state built from the scenario
    so a simulator can be executed any number of times.

    Args:
        scenario (:obj:`Scenario`): The scenario to simulate.
        demands_satisfied (bool): True, if demands shall be satisfied with
            resources available in the simulation; otherwise all demands are
            logged as unsatisfied.
        packing_demands_added (bool): True, if demands for packing material
            (generic COS 5) shall be added to unsatisfied demands.
        items_repaired (bool): True, if demands for the parts in
            `repaired_items` shall be repaired rather than replaced.
        repaired_items (dict): Items to repair by mission index.
    """

    # pylint: disable=too-many-instance-attributes,too-many-public-methods

    def __init__(
        self,
        scenario: Scenario,
        *,
        demands_satisfied: bool = True,
        packing_demands_added: bool = False,
        items_repaired: bool = False,
        repaired_items: Optional[Dict[int, List[RepairItem]]] = None,
        part_failures: Optional[PartFailureMode] = None,
        seed: Optional[int] = None,
    ):
        self.scenario = scenario
        #: Model of part failures (default: the scenario configuration).
        self.part_failures = (
            PartFailureMode(part_failures)
            if part_failures is not None
            else scenario.configuration.part_failures
        )
        #: Seed of random part failures (default: the scenario configuration).
        self.seed = seed if seed is not None else scenario.configuration.random_seed
        self._rng = np.random.default_rng(self.seed)
        #: Failures of parts over each interval of time.
        self.failure_records: List[FailureRecord] = []
        self.demands_satisfied = demands_satisfied
        self.packing_demands_added = packing_demands_added
        self.items_repaired = items_repaired
        #: Items to repair (rather than replace) by mission index.
        self.repaired_items: Dict[int, List[RepairItem]] = (
            repaired_items if repaired_items is not None else {}
        )
        #: Simulation state (available after a simulation is initialized).
        self.state: Optional[State] = None
        #: Simulation time (days) relative to the scenario start.
        self.time = 0.0
        #: Time (days) elapsed between the previous and the current event.
        self.duration = 0.0
        #: Event currently being executed.
        self.event: Optional[SimEvent] = None
        self.warnings: List[SimWarning] = []
        self.spatial_errors: List[SimSpatialError] = []
        self.unsatisfied_demands: List[SimDemand] = []
        self.scavenged_parts: List[SimScavenge] = []
        self.repaired_parts: List[SimRepair] = []
        #: Changes to the contents of the integral tanks of vehicles.
        self.propellant_flows: List[PropellantFlow] = []
        #: Energy balance of each power group over each interval of time.
        self.power_records: List[PowerRecord] = []
        #: Operation of each ISRU process over each interval of time.
        self.isru_records: List[ISRURecord] = []
        self._isru_warnings: set = set()
        self._power_warnings: set = set()
        #: Time at which each power group arrived at its location.
        self._power_arrivals: Dict[tuple, float] = {}
        #: Crew members (and missions) whose carried consumables were demanded.
        self._consumables_departed: set = set()
        self._consumables_missions: set = set()
        #: Costs incurred by creating elements and by transports.
        self.cost_records: List[CostRecord] = []
        self._costed: set = set()
        #: Time of the last departure along each edge (by unique identifier).
        self._departures: Dict[UUID, float] = {}
        self._retired_warnings: set = set()
        self._events: List[Tuple[float, int, str, int, SimEvent]] = []
        self._sequence = 0
        self._repaired_items: Dict[int, List[RepairItem]] = {}
        self._item_demands: Dict[object, Dict[SimResource, float]] = defaultdict(dict)

    @property
    def settings(self) -> Settings:
        """The numerical precision and analysis options."""
        return self.state.settings

    @property
    def errors(self) -> List[SimError]:
        """The spatial errors and unsatisfied demands in order of time."""
        return sorted(
            [*self.spatial_errors, *self.unsatisfied_demands], key=lambda e: e.time
        )

    # ------------------------------------------------------------ event queue

    def schedule(self, event: SimEvent):
        """
        Schedules an event for future execution. Coincident events are
        executed in order of priority and then name.

        Args:
            event (:obj:`SimEvent`): The event.
        """
        event.time = self.settings.round_time(event.time)
        heapq.heappush(
            self._events,
            (event.time, event.priority, event.name, self._sequence, event),
        )
        self._sequence += 1

    def _peek_event(self) -> Optional[SimEvent]:
        return self._events[0][4] if self._events else None

    @property
    def pending_events(self) -> List[SimEvent]:
        """The scheduled events which have not been executed (in no particular order)."""
        return [entry[4] for entry in self._events]

    def execute_event(self, event: SimEvent):
        """
        Executes an event at the current simulation time, logging any
        errors. The event is removed from the scheduled events.

        Args:
            event (:obj:`SimEvent`): The event.
        """
        self._events = [entry for entry in self._events if entry[4] is not event]
        heapq.heapify(self._events)
        self.event = event
        self._execute_event()

    def simulate(self):
        """
        Executes the simulation.
        """
        raise NotImplementedError()

    def initialize_simulation(self):
        """
        Resets this simulator and schedules the missions of a new state.
        """
        self._events.clear()
        self._sequence = 0
        self.spatial_errors.clear()
        self.unsatisfied_demands.clear()
        self.warnings.clear()
        self.scavenged_parts.clear()
        self.repaired_parts.clear()
        self.propellant_flows.clear()
        self.power_records.clear()
        self.isru_records.clear()
        self._isru_warnings.clear()
        self.failure_records.clear()
        self._rng = np.random.default_rng(self.seed)
        self._power_warnings.clear()
        self._power_arrivals.clear()
        self._consumables_departed.clear()
        self._consumables_missions.clear()
        self.cost_records.clear()
        self._costed.clear()
        self._departures.clear()
        self._retired_warnings.clear()
        self._item_demands.clear()
        self.time = 0.0
        self.duration = 0.0
        self.event = None
        self.state = State(self.scenario)
        self._repaired_items = {
            index: [item.copy() for item in items]
            for index, items in self.repaired_items.items()
        }
        for mission in self.state.missions:
            self.schedule(MissionEvent(mission))
            # identify the crew of each mission in the initial state
            _ = mission.crew_members

    def _next_event(self):
        """Advances the simulation time to the next event."""
        self.event = heapq.heappop(self._events)[4]
        self.duration = self.event.time - self.time
        self.time = self.event.time

    def _log_error(self, error: SimError):
        if isinstance(error, SimDemand):
            self.unsatisfied_demands.append(error)
        else:
            logger.warning("%.3f: %s", error.time, error)
            self.spatial_errors.append(error)

    def _execute_event(self):
        """Executes the current event, logging any errors."""
        try:
            self.event.execute(self)
        except SimError as error:
            self._log_error(error)

    # ------------------------------------------------------------- propellant

    def record_propellant(
        self,
        tank: SimResourceTank,
        kind: PropellantFlowKind,
        amount: float,
        event: Optional[SimEvent] = None,
        attributed: bool = True,
    ):
        """
        Records a change to the contents of an integral tank of a vehicle.
        Changes to tanks which do not belong to a vehicle are ignored.

        Args:
            tank (:obj:`SimResourceTank`): The tank (after the change).
            kind (:obj:`PropellantFlowKind`): The kind of change.
            amount (float): The amount (units) changed.
            event (:obj:`SimEvent`): The causing event (default: the current event).
            attributed (bool): False, if no event causes the change.
        """
        vehicle = tank.vehicle
        # empty tanks are recorded when loaded to report their history
        if vehicle is None or (amount == 0 and kind != PropellantFlowKind.LOADED):
            return
        if event is None and attributed:
            event = self.event
        self.propellant_flows.append(
            PropellantFlow(
                time=self.time,
                vehicle_id=vehicle.id,
                vehicle_name=vehicle.name,
                tank_key=tank.key,
                tank_role=tank.role,
                resource_name=None if tank.resource is None else tank.resource.name,
                unit_mass=1.0 if tank.resource is None else tank.resource.unit_mass,
                kind=PropellantFlowKind(kind),
                amount=amount,
                amount_after=tank._amount,  # pylint: disable=protected-access
                max_amount=tank._max_amount,  # pylint: disable=protected-access
                event_name=None if event is None else event.name,
            )
        )

    def _handle_boiloff(self):
        """
        Removes the resources lost to boiloff from the integral tanks of all
        vehicles over the elapsed duration. Vehicles on the surface of Earth
        are assumed to be topped off before launch.
        """
        for element in self.state.network.elements:
            tanks = getattr(element, "fuel_tanks", None)
            if not tanks:
                continue
            location = element.location
            if (
                isinstance(location, SimNode)
                and location.is_surface
                and location.body == Body.EARTH
            ):
                continue
            for tank in tanks:
                loss = tank.apply_boiloff(self.duration)
                if loss > 0:
                    self.record_propellant(
                        tank, PropellantFlowKind.BOILOFF, loss, attributed=False
                    )

    # ------------------------------------------------------------------ power

    def _power_groups(self) -> List[Tuple[SimLocation, str, str, List[SimElement]]]:
        """
        Lists the groups of elements which share power: each top-level element
        with its (nested) contents, except that the grid-connected top-level
        elements at a surface node form one group. Groups on the surface of
        Earth (with unconstrained power) are omitted.

        Returns:
            [(location, key, name, elements)]: The power groups.
        """
        groups: Dict[str, Tuple[SimLocation, str, str, List[SimElement]]] = {}
        for location in self.state.network.locations:
            surface = isinstance(location, SimNode) and location.is_surface
            if surface and location.body == Body.EARTH:
                continue
            for element in location.contents:
                members = [element]
                if isinstance(element, ElementContainer):
                    members.extend(element.complete_contents)
                if not any(member.has_power for member in members):
                    continue
                if surface and element.grid_connected:
                    key, name = f"grid:{location.id}", f"{location.name} Grid"
                else:
                    key, name = f"element:{element.id}", element.name
                group = groups.setdefault(key, (location, key, name, []))
                group[3].extend(members)
        return list(groups.values())

    def _handle_power(self, plans: Optional[List[_ISRUPlan]] = None):
        """
        Balances the power generated and consumed by each power group over
        the elapsed duration, charging or discharging its energy storage, and
        warns (once per group) of energy deficits and of storage which cannot
        survive the longest night at a surface node. ISRU processes consume
        the power which remains after other consumption (proportionally to
        their requests) without discharging energy storage.

        Args:
            plans ([_ISRUPlan]): The planned ISRU processes (the rates of which
                are reduced to the available power).
        """
        hours = 24 * self.duration
        plans = plans or []
        for location, key, name, members in self._power_groups():
            illumination = getattr(location, "illumination", 1.0)
            constant = solar = consumption = 0.0
            for member in members:
                state = member.current_state
                if state is None:
                    continue
                consumption += state.power_consumption
                if state.generation_type == PowerGenerationType.SOLAR:
                    solar += state.power_generation
                else:
                    constant += state.power_generation
            generation = constant + illumination * solar
            consumption += self._allocate_isru_power(
                [p for p in plans if any(p.element is m for m in members)],
                generation - consumption,
            )
            capacity = sum(member.energy_capacity for member in members)
            stored = sum(member.energy for member in members)
            energy = stored + (generation - consumption) * hours
            deficit = max(0.0, -energy)
            energy = min(capacity, max(0.0, energy))
            for member in members:
                if capacity > 0:
                    member.energy = energy * member.energy_capacity / capacity
            # a stay shorter than a synodic day can be scheduled in sunlight
            arrival = self._power_arrivals.setdefault(
                (key, location.id), self.time - self.duration
            )
            synodic = SYNODIC_DAYS.get(getattr(location, "body", None), 1.0)
            night = getattr(location, "max_night_duration", 0.0)
            night_energy = (
                max(0.0, consumption - constant) * night if solar > 0 else 0.0
            )
            stays_overnight = self.time - arrival >= synodic
            self.power_records.append(
                PowerRecord(
                    time=self.time,
                    duration=self.duration,
                    location_id=location.id,
                    location_name=location.name,
                    key=key,
                    name=name,
                    elements=[m.name for m in members if m.has_power],
                    illumination=illumination,
                    generation=generation,
                    consumption=consumption,
                    energy=energy,
                    capacity=capacity,
                    deficit=deficit,
                    night_energy=night_energy,
                    stays_overnight=stays_overnight,
                )
            )
            if deficit > 0 and ("deficit", key) not in self._power_warnings:
                self._power_warnings.add(("deficit", key))
                self.warnings.append(
                    SimWarning(
                        self.time,
                        None,
                        f"{name} at {location.name} has a power deficit of "
                        f"{deficit:,.1f} kWh (generation {generation:,.1f} kW, "
                        f"consumption {consumption:,.1f} kW).",
                    )
                )
            if (
                stays_overnight
                and night_energy > capacity
                and ("night", key) not in self._power_warnings
            ):
                self._power_warnings.add(("night", key))
                self.warnings.append(
                    SimWarning(
                        self.time,
                        None,
                        f"{name} at {location.name} requires {night_energy:,.1f} kWh "
                        f"to survive the longest night ({night:,.0f} h) but stores "
                        f"{capacity:,.1f} kWh.",
                    )
                )

    # ------------------------------------------------------------------- ISRU

    @staticmethod
    def _allocate_isru_power(plans: List[_ISRUPlan], surplus: float) -> float:
        """
        Reduces the rates of ISRU processes to the surplus power of their
        group (proportionally to their requests).

        Returns:
            float: The power (kW) consumed by the processes.
        """
        requested = sum(p.rate * p.model.power for p in plans)
        if requested <= 0:
            return 0.0
        fraction = min(1.0, max(0.0, surplus) / requested)
        if fraction < 1:
            for plan in plans:
                if plan.model.power > 0:
                    plan.rate *= fraction
                    plan.limit, plan.resource = "Power", None
        return sum(p.rate * p.model.power for p in plans)

    @staticmethod
    def _isru_holders(element: SimElement) -> List[SimElement]:
        """
        Lists the tanks and resource containers available to an ISRU process
        of an element: the element and its contents, its carrier and the
        carrier's contents, and the elements (and contents) at its location,
        including the integral tanks of vehicles. Outputs are stored in the
        element itself (if it is a resource container) or in the tanks and
        containers which hold the output resource.
        """
        candidates: List[SimElement] = []

        def add(item):
            candidates.append(item)
            if isinstance(item, ElementContainer):
                candidates.extend(item.complete_contents)

        add(element)
        if isinstance(element.container, SimElement):
            add(element.container)
        if element.location is not None:
            for item in element.location.contents:
                add(item)
        holders, seen = [], set()
        for candidate in candidates:
            for holder in [candidate, *(getattr(candidate, "fuel_tanks", None) or [])]:
                if id(holder) in seen or not isinstance(
                    holder, (SimResourceContainer, SimResourceTank)
                ):
                    continue
                seen.add(id(holder))
                holders.append(holder)
        return holders

    def _isru_material_rate(self, plan: _ISRUPlan, holders: List[SimElement]):
        """
        Limits the rate of an ISRU process to its available inputs and output
        storage over the elapsed duration.
        """
        for constraint, rates in (
            ("Input", plan.model.inputs),
            ("Output Storage", plan.model.outputs),
        ):
            for rate in rates:
                required = rate.raw_amount * self.duration
                if required <= 0:
                    continue
                if constraint == "Input":
                    available = sum(h.get_amount(rate.resource) for h in holders)
                else:
                    available = sum(
                        h.get_space(rate.resource)
                        for h in holders
                        if h is plan.element or h.holds(rate.resource)
                    )
                fraction = max(0.0, min(1.0, available / required))
                if fraction < plan.rate:
                    plan.rate = fraction
                    plan.limit, plan.resource = constraint, rate.resource

    def _plan_isru(self) -> List[_ISRUPlan]:
        """Plans the ISRU processes of elements in their current states."""
        plans = []
        for element in self.state.network.elements:
            state = element.current_state
            if state is None:
                continue
            for model in state.demand_models:
                if isinstance(model, SimISRUProcessModel):
                    plan = _ISRUPlan(element, model)
                    self._isru_material_rate(plan, self._isru_holders(element))
                    plans.append(plan)
        return plans

    def _transfer_isru(self, plan: _ISRUPlan, holders, demands, sign: int):
        """
        Draws (sign 1) inputs from or deposits (sign -1) outputs to holders.

        Returns:
            (dict, dict): The amount (units) and mass (kg) by resource name.
        """
        amounts, masses = {}, {}
        for demand in demands:
            required = demand.raw_amount * self.duration * plan.rate
            remaining = required
            for holder in holders:
                if remaining <= 0:
                    break
                if sign > 0:
                    moved = holder.draw(demand.resource, remaining)
                elif holder is plan.element or holder.holds(demand.resource):
                    moved = holder.deposit(demand.resource, remaining)
                else:
                    continue
                remaining -= moved
                if isinstance(holder, SimResourceTank) and moved > 0:
                    self.record_propellant(
                        holder,
                        PropellantFlowKind.CONSUMED,
                        sign * moved,
                        attributed=False,
                    )
            amount = required - max(0.0, remaining)
            amounts[demand.resource.name] = amount
            masses[demand.resource.name] = amount * demand.resource.unit_mass
        return amounts, masses

    def _handle_isru(self, plans: List[_ISRUPlan]):
        """
        Operates the planned ISRU processes over the elapsed duration:
        consumes inputs, stores outputs, and records the operation. Warns
        (once per process and constraint) if a process cannot operate.
        """
        for plan in plans:
            element, model = plan.element, plan.model
            holders = self._isru_holders(element)
            # inputs or storage may have been used by a prior process
            self._isru_material_rate(plan, holders)
            inputs, input_masses = self._transfer_isru(plan, holders, model.inputs, 1)
            outputs, output_masses = self._transfer_isru(
                plan, holders, model.outputs, -1
            )
            location = element.location
            self.isru_records.append(
                ISRURecord(
                    time=self.time,
                    duration=self.duration,
                    element_id=element.id,
                    element_name=element.name,
                    process=model.name,
                    location_id=None if location is None else location.id,
                    location_name=None if location is None else location.name,
                    rate=plan.rate,
                    limit=plan.limit if plan.rate < 1 else None,
                    power=plan.rate * model.power,
                    inputs=inputs,
                    outputs=outputs,
                    input_masses=input_masses,
                    output_masses=output_masses,
                )
            )
            if plan.rate <= 0:
                self._warn_isru(plan)

    def _warn_isru(self, plan: _ISRUPlan):
        key = (plan.element.id, plan.model.name, plan.limit)
        if key in self._isru_warnings:
            return
        self._isru_warnings.add(key)
        if plan.limit == "Power":
            reason = "has no surplus power"
        elif plan.limit == "Input":
            reason = f"has no {plan.resource.name} input"
        else:
            reason = f"has no storage for {plan.resource.name}"
        self.warnings.append(
            SimWarning(
                self.time,
                None,
                f"ISRU process {plan.model.name} of {plan.element.name} "
                f"cannot operate: it {reason}.",
            )
        )

    # ------------------------------------------------------------ reliability

    def _part_failures(self, element: SimElement) -> DemandSet:
        """
        Generates the demands for spare parts of the failures of the parts of
        an active element over the elapsed duration: each unit of a part with
        a mean time to failure fails at a constant rate while it operates
        (for its duty cycle while the element is active), and a failed unit
        demands a spare. Elements on the surface of Earth do not fail.

        Returns:
            :obj:`DemandSet`: The demands for spare parts.
        """
        demands = DemandSet()
        state = element.current_state
        if (
            self.part_failures is None
            or state is None
            or state.state_type != StateType.ACTIVE
        ):
            return demands
        location = element.location
        if (
            isinstance(location, SimNode)
            and location.is_surface
            and location.body == Body.EARTH
        ):
            return demands
        for application in element.parts:
            if application.mean_time_to_failure <= 0 or application.quantity <= 0:
                continue
            hours = 24 * self.duration * application.duty_cycle * application.quantity
            expected = hours / application.mean_time_to_failure
            if self.part_failures == PartFailureMode.RANDOM:
                failures = float(self._rng.poisson(expected))
            else:
                failures = expected
            self.failure_records.append(
                FailureRecord(
                    time=self.time,
                    duration=self.duration,
                    element_id=element.id,
                    element_name=element.name,
                    part_name=application.part.name,
                    location_id=None if location is None else location.id,
                    location_name=None if location is None else location.name,
                    operating_hours=hours,
                    expected=expected,
                    failures=failures,
                )
            )
            if failures > 0:
                demands.add(Demand(application.part, failures))
        return demands

    # ----------------------------------------------------- cost and lifetime

    def record_cost(self, event: Optional[SimEvent], category: str, item: str, amount):
        """
        Records a cost incurred by an event.

        Args:
            event (:obj:`SimEvent`): The causing event.
            category (str): The category ("Element" or "Transport").
            item (str): The name of the costed element or edge.
            amount (float): The cost (millions of US dollars).
        """
        mission = None
        if event is not None:
            index = event.root.mission_index
            if index is not None and 0 <= index < len(self.state.missions):
                mission = self.state.missions[index]
        self.cost_records.append(
            CostRecord(
                time=self.time,
                mission=None if mission is None else mission.name,
                category=category,
                item=item,
                amount=amount,
                event_name=None if event is None else event.name,
            )
        )

    def record_creation(self, event: SimEvent, element: SimElement):
        """
        Records the creation of an element (and its nested contents): its
        creation time and its unit cost (once per element).
        """
        elements = [element]
        if isinstance(element, ElementContainer):
            elements.extend(element.complete_contents)
        for item in elements:
            if item.created_time is None:
                item.created_time = self.time
            if item.unit_cost and item.id not in self._costed:
                self._costed.add(item.id)
                self.record_cost(event, "Element", item.name, item.unit_cost)

    def record_departure(self, event: SimEvent, edge: SimEdge):
        """
        Records a transport departing along an edge: its cost and a warning
        if it departs sooner than the minimum departure interval.
        """
        interval = edge.min_departure_interval
        previous = self._departures.get(edge.id)
        if interval and previous is not None and self.time - previous < interval - 1e-9:
            self.warnings.append(
                SimWarning(
                    self.time,
                    event,
                    f"departs along {edge} {self.time - previous:,.1f} days after the "
                    f"previous transport (minimum interval {interval:,.1f} days).",
                )
            )
        self._departures[edge.id] = self.time
        if edge.cost_per_transport:
            self.record_cost(event, "Transport", edge.name, edge.cost_per_transport)

    def _check_design_life(self):
        """Warns (once per element) of elements used beyond their design life."""
        for element in self.state.network.elements:
            life = element.design_life
            if not life or element.created_time is None:
                continue
            age = (self.time - element.created_time) / 365.25
            if age > life + 1e-9 and element.id not in self._retired_warnings:
                self._retired_warnings.add(element.id)
                self.warnings.append(
                    SimWarning(
                        self.time,
                        None,
                        f"{element} is used beyond its design life of {life:,.1f} "
                        f"years (age {age:,.1f} years).",
                    )
                )

    # ------------------------------------------------------- crew consumables

    def _handle_crew_consumables(self):
        """
        Generates time-phased crew consumables: the daily demands of the crew
        of each mission over the elapsed duration where they are (outside
        the surface of Earth), and the demands carried by each crew member
        (with reserves) and shared by the mission when they first leave the
        surface of Earth.
        """
        for mission in self.state.missions:
            models = [m for m in mission.demand_models if hasattr(m, "daily_demands")]
            if not models:
                continue
            groups: Dict[UUID, List[SimElement]] = {}
            for member in mission.crew_members:
                location = member.location
                if location is None or (
                    isinstance(location, SimNode)
                    and location.is_surface
                    and location.body == Body.EARTH
                ):
                    continue
                if member.id not in self._consumables_departed:
                    self._consumables_departed.add(member.id)
                    for model in models:
                        demands = model.crew_demands(1)
                        if mission.index not in self._consumables_missions:
                            demands.add_all(model.mission_demands())
                        self._execute_crew_demands(mission, [member], demands)
                    self._consumables_missions.add(mission.index)
                # crew members leave Earth by an event, so they were away
                # from Earth for the whole elapsed duration
                if self.duration > 0:
                    groups.setdefault(member.container.id, []).append(member)
            for members in groups.values():
                on_edge = isinstance(members[0].location, SimEdge)
                for model in models:
                    if on_edge and model.transit_demands_omitted:
                        continue
                    self._execute_crew_demands(
                        mission,
                        members,
                        model.daily_demands(len(members) * self.duration),
                    )

    def _execute_crew_demands(self, mission, members, demands: DemandSet):
        """Executes the crew consumables demands of crew members at their location."""
        location = members[0].location
        demands = self._discretize_demands(demands, None, location)
        if len(demands) == 0:
            return
        event = DemandEvent(
            time=self.time,
            priority=LAST_PRIORITY,
            name=f"Crew Consumables for {mission}",
            element=members[0],
            location=location,
            demands=demands,
        )
        try:
            event.execute(self)
        except SimError as error:
            self._log_error(error)

    # ---------------------------------------------------------------- demands

    def _handle_demands(self):
        """
        Removes boiloff losses and generates and executes the demands of all
        elements over the elapsed duration and schedules mission-level demands
        at the start of a mission.
        """
        if self.settings.time_phased_consumables:
            self._handle_crew_consumables()
        if self.duration > 0:
            self._handle_boiloff()
            plans = self._plan_isru()
            self._handle_power(plans)
            self._handle_isru(plans)
            self._check_design_life()
            for element in self.state.network.elements:
                demands = element.generate_demands(self.duration, self)
                demands.add_all(self._part_failures(element))
                demands = self._discretize_demands(demands, element, element.location)
                demands = self._repair_demands(demands, element)
                if len(demands) > 0:
                    event = DemandEvent(
                        time=self.time,
                        name=f"Demand Event for {element}",
                        element=element,
                        location=element.location,
                        demands=demands,
                    )
                    try:
                        event.execute(self)
                    except SimError as error:
                        self._log_error(error)
        if isinstance(self.event, MissionEvent):
            mission = self.event.mission
            self.schedule(
                DemandEvent(
                    time=self.time + mission.transit_duration,
                    priority=LAST_PRIORITY,
                    parent=self.event,
                    name=f"Demand Event for {mission}",
                    location=mission.destination,
                    demands=self._discretize_demands(
                        mission.generate_demands(self), None, mission.destination
                    ),
                )
            )

    def _discretize_demands(
        self,
        demands: DemandSet,
        element: Optional[SimElement],
        location: Optional[SimLocation],
    ) -> DemandSet:
        """
        Aggregates fractional demands for discrete resources (items) to whole
        units at the level of an element, a location, or the scenario.
        """
        discretization = self.settings.item_discretization
        key = None
        if discretization == ItemDiscretizationType.DISCRETIZE_PER_ELEMENT:
            key = element
        elif discretization == ItemDiscretizationType.DISCRETIZE_PER_LOCATION:
            key = location
        elif discretization == ItemDiscretizationType.DISCRETIZE_PER_SCENARIO:
            key = "scenario"
        if key is not None:
            aggregation = self.settings.item_aggregation
            item_demands = self._item_demands[key]
            for demand in demands:
                if not demand.resource.is_item:
                    continue
                accumulated = item_demands.get(demand.resource, 0.0) + demand.amount
                units = 0
                while accumulated >= aggregation:
                    units += 1
                    accumulated -= 1
                demand.amount = units
                item_demands[demand.resource] = accumulated
        demands.clean()
        return demands

    def _repair_demands(self, demands: DemandSet, element: SimElement) -> DemandSet:
        """
        Replaces demands for repairable parts of an element with demands for
        the mass (generic COS 4) required to repair them.
        """
        if self.items_repaired and self._repaired_items:
            last_time = 0.0
            for mission in self.state.missions:
                items = self._repaired_items.get(mission.index)
                end_time = mission.start_time + mission.duration
                # NOTE: uses the same time window as the tabulation of repairable
                # demands (the reference implementation excludes demands at
                # the end of a mission which are then never repaired)
                if items is None or not last_time < self.time <= end_time:
                    continue
                if mission.is_crewed:
                    last_time = end_time
                for item in items:
                    if item.element != element or not item.demand.resource.is_item:
                        continue
                    for demand in demands:
                        if (
                            item.demand.resource != demand.resource
                            or item.demand.amount <= 0
                        ):
                            continue
                        amount = min(demand.amount, item.demand.amount)
                        if amount <= 0:
                            continue
                        self._record_repair(
                            mission, element, item, demand.resource, amount
                        )
                        demand.amount = demand.amount - amount
                        demands.add(
                            Demand(
                                self.state.get_resource(ClassOfSupply.COS_4),
                                item.unit_mass_to_repair * amount,
                            )
                        )
                        item.demand.amount = item.demand.amount - amount
        demands.clean()
        return demands

    def _record_repair(
        self,
        mission: SimMission,  # pylint: disable=unused-argument
        element: SimElement,
        item: RepairItem,
        resource: SimResource,
        amount: float,
    ):
        """Records the repair of an amount of a part."""
        self.repaired_parts.append(
            SimRepair(
                self.time,
                resource,
                amount,
                amount * item.unit_mean_repair_time,
                amount * item.unit_mass_to_repair,
                element.location,
                element,
            )
        )

    # --------------------------------------------------------- demand history

    def get_demand_history(self, source) -> List[SimDemand]:
        """
        Gets the unsatisfied demands of an element, a location, or a mission.

        Args:
            source (:obj:`SimElement`, :obj:`SimLocation`, or :obj:`SimMission`):
                The source of the demands.

        Returns:
            :obj:`List[SimDemand]`: The unsatisfied demands.
        """
        if isinstance(source, SimMission):
            start_time = source.start_time
            end_time = start_time + source.duration
            return [
                d for d in self.unsatisfied_demands if start_time < d.time <= end_time
            ]
        if isinstance(source, SimElement):
            return [d for d in self.unsatisfied_demands if d.element == source]
        return [d for d in self.unsatisfied_demands if d.location == source]

    def get_demands(
        self,
        source,
        *,
        element: Optional[SimElement] = None,
        mission_level: bool = False,
        class_of_supply: Optional[ClassOfSupply] = None,
    ) -> DemandSet:
        """
        Aggregates the unsatisfied demands of an element, a location, or a mission.

        Args:
            source (:obj:`SimElement`, :obj:`SimLocation`, or :obj:`SimMission`):
                The source of the demands.
            element (:obj:`SimElement`): Restricts demands to those generated
                by an element.
            mission_level (bool): True, to restrict demands to those generated
                by mission-level (rather than element) demand models.
            class_of_supply (:obj:`ClassOfSupply`): Restricts demands to a
                class of supply (and its sub-classes).

        Returns:
            :obj:`DemandSet`: The aggregated demands.
        """
        demands = DemandSet()
        for sim_demand in self.get_demand_history(source):
            if mission_level and sim_demand.element is not None:
                continue
            if element is not None and sim_demand.element != element:
                continue
            for demand in sim_demand.demands:
                if (
                    class_of_supply is None
                    or demand.resource.class_of_supply.is_instance_of(class_of_supply)
                ):
                    demands.add(demand)
        return demands


class MiniSimulator(Simulator):
    """
    Simulator which records the location of each element before and after
    every event.
    """

    def __init__(self, scenario: Scenario, **kwargs):
        super().__init__(scenario, **kwargs)
        self.location_history: List[LocationSnapshot] = []

    def simulate(self):
        self.initialize_simulation()
        self.location_history.clear()
        while self._peek_event() is not None:
            self._next_event()
            self.location_history.append(
                LocationSnapshot(self.time, self.state.network)
            )
            self._handle_demands()
            self._execute_event()
            self.location_history.append(
                LocationSnapshot(self.time, self.state.network)
            )


class PreSimulator(Simulator):
    """
    Simulator which executes a scenario up to a specified time and priority,
    e.g., to inspect the state in which an event will be executed.
    """

    def simulate(
        self,
        time: float = math.inf,
        priority: int = LAST_PRIORITY,
        reset: bool = True,
    ):  # pylint: disable=arguments-differ
        """
        Executes the simulation up to (but not including) events at a
        specified time with a specified priority.

        Args:
            time (float): The time (days) at which to stop.
            priority (int): The priority of coincident events at which to stop.
            reset (bool): True, to restart the simulation; otherwise continue
                from the current state.
        """
        if self.state is None or reset:
            self.initialize_simulation()
        while self._peek_event() is not None:
            event = self._peek_event()
            if event.time > time:
                break
            if (
                not isinstance(event, MissionEvent)
                and event.time == time
                and event.priority >= priority
            ):
                break
            self._next_event()
            self._handle_demands()
            self._execute_event()
        if math.isfinite(time):
            self.duration = time - self.time
            self.time = time
            self.event = None
            self._handle_demands()

    def simulate_to_event(self, event: SimEvent, reset: bool = True):
        """
        Executes the simulation up to (but not including) an event.

        Args:
            event (:obj:`SimEvent`): The event at which to stop.
            reset (bool): True, to restart the simulation.
        """
        self.simulate(event.time, event.priority, reset)


class DemandSimulator(Simulator):
    """
    Simulator which logs demands and aggregates them to the transports (supply
    edges) and arrivals (supply points) from which they could be supplied.
    """

    def __init__(self, scenario: Scenario, **kwargs):
        super().__init__(scenario, **kwargs)
        #: Repairable demands by mission index in order of logged time.
        self.unsorted_repair_items: Dict[int, List[RepairItem]] = {}
        #: Repairable demands by mission index in order of repair value.
        self.sorted_repair_items: Dict[int, List[RepairItem]] = {}
        #: Transports in order of decreasing arrival time.
        self.supply_edges: List[SupplyEdge] = []
        #: Arrivals in order of decreasing time.
        self.supply_points: List[SupplyPoint] = []
        self._node_demands: Dict[int, DemandSet] = {}
        self._edge_demands: Dict[int, DemandSet] = {}
        #: Demands which could not be assigned to a supply point or supply edge.
        self.unassigned_demands: List[SimDemand] = []

    @property
    def aggregated_node_demands(self) -> List[Tuple[SupplyPoint, DemandSet]]:
        """The demands aggregated to each supply point."""
        return [(p, self._node_demands[id(p)]) for p in self.supply_points]

    @property
    def aggregated_edge_demands(self) -> List[Tuple[SupplyEdge, DemandSet]]:
        """The demands aggregated to each supply edge."""
        return [(e, self._edge_demands[id(e)]) for e in self.supply_edges]

    def simulate(self):
        self.initialize_simulation()
        self.unsorted_repair_items = {m.index: [] for m in self.state.missions}
        self.sorted_repair_items = {m.index: [] for m in self.state.missions}
        self.supply_edges = []
        self.supply_points = []
        self._node_demands = {}
        self._edge_demands = {}
        self.unassigned_demands = []
        while self._peek_event() is not None:
            self._next_event()
            if isinstance(self.event, TransportEvent) and self.event.edge is not None:
                self._add_supply_edge(self.event)
            self._handle_demands()
            self._execute_event()
        self.supply_edges.sort(key=lambda e: (-e.end_time, e.origin.index))
        self.supply_points.sort(key=lambda p: (-p.time, p.node.index))
        self._tabulate_repairable_demands()
        self._aggregate_demands()

    def _add_supply_edge(self, event: TransportEvent):
        duration = event.duration
        if not math.isfinite(duration):
            return
        edge = SupplyEdge(
            event.edge,
            isinstance(event, SurfaceTransportEvent) and event.is_reversed,
            event.time,
            self.settings.round_time(event.time + duration),
            [
                ElementSnapshot.create(e)
                for e in event.elements
                if isinstance(e, SimCarrier)
            ],
        )
        self.supply_edges.append(edge)
        self._edge_demands[id(edge)] = DemandSet()
        if not any(
            p.node == edge.point.node and p.time == edge.point.time
            for p in self.supply_points
        ):
            self.supply_points.append(edge.point)
            self._node_demands[id(edge.point)] = DemandSet()

    def _tabulate_repairable_demands(self):
        last_end_time = 0.0
        for mission in self.state.missions:
            if not mission.is_crewed:
                continue
            start_time = last_end_time
            end_time = mission.start_time + mission.duration
            last_end_time = end_time
            items = self.unsorted_repair_items[mission.index]
            for sim_demand in self.unsatisfied_demands:
                if (
                    sim_demand.element is None
                    or not start_time < sim_demand.time <= end_time
                ):
                    continue
                for demand in sim_demand.demands:
                    if not demand.resource.is_item:
                        continue
                    for application in sim_demand.element.parts:
                        if (
                            application.part == demand.resource
                            and application.mean_time_to_repair > 0
                        ):
                            items.append(RepairItem(demand, sim_demand.element))
                            break
            self.sorted_repair_items[mission.index] = sorted(
                items, key=lambda i: i.repair_value
            )

    def _aggregate_demands(self):
        for sim_demand in self.unsatisfied_demands:
            location = sim_demand.location
            if isinstance(location, SimNode):
                point = None
                for candidate in self.supply_points:
                    if (
                        candidate.node == location
                        and candidate.time <= sim_demand.time
                        and (point is None or candidate.time > point.time)
                    ):
                        point = candidate
                if point is not None:
                    self._node_demands[id(point)].add_all(sim_demand.demands)
                elif not (location.is_surface and location.body == Body.EARTH):
                    logger.warning(
                        "No supply point found to satisfy demands! %s %s",
                        sim_demand.time,
                        sim_demand.demands,
                    )
                    self.unassigned_demands.append(sim_demand)
            elif isinstance(location, SimEdge):
                edge = None
                for candidate in self.supply_edges:
                    if (
                        candidate.edge == location
                        and candidate.start_time
                        <= sim_demand.time
                        <= candidate.end_time
                    ):
                        edge = candidate
                if edge is not None:
                    self._edge_demands[id(edge)].add_all(sim_demand.demands)
                else:
                    logger.warning(
                        "No supply edge found to satisfy demands! %s %s",
                        sim_demand.time,
                        sim_demand.demands,
                    )
                    self.unassigned_demands.append(sim_demand)


class FullSimulator(Simulator):
    """
    Simulator which records the network history and measures of effectiveness.
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self, scenario: Scenario, **kwargs):
        kwargs.setdefault("packing_demands_added", False)
        kwargs.setdefault("items_repaired", True)
        super().__init__(scenario, **kwargs)
        #: History of the elements of the network at each time step.
        self.network_history = NetworkHistory()
        self.crew_surface_days_history: List[MoeCrewSurfaceDays] = []
        self.crew_time_history: List[MoeCrewTime] = []
        self.exploration_mass_delivered_history: List[MoeExplorationMassDelivered] = []
        self.launch_mass_history: List[MoeLaunchMass] = []
        self.up_mass_capacity_utilization_history: List[MoeMassCapacityUtilization] = []
        self.down_mass_capacity_utilization_history: List[
            MoeMassCapacityUtilization
        ] = []
        self.exploration_capability_history: List[MoeExplorationCapability] = []

    def simulate(self):
        self.initialize_simulation()
        # only the full simulator loads manifested containers so the demands
        # logged by other simulators do not depend on the manifest
        for message in self.state.manifest_warnings:
            self.warnings.append(SimWarning(0.0, None, message))
        for event in self.state.manifest_events:
            self.schedule(event)
        self.network_history = NetworkHistory()
        self.crew_surface_days_history.clear()
        self.crew_time_history.clear()
        self.exploration_mass_delivered_history.clear()
        self.launch_mass_history.clear()
        self.up_mass_capacity_utilization_history.clear()
        self.down_mass_capacity_utilization_history.clear()
        self.exploration_capability_history.clear()
        self._record_network()
        while self._peek_event() is not None:
            self._next_event()
            if self.duration > 0:
                self._record_crew_measures()
            if isinstance(self.event, (SpaceTransportEvent, FlightTransportEvent)):
                self._record_transport_measures(self.event)
            self._handle_demands()
            self._execute_event()
            next_event = self._peek_event()
            if next_event is None or next_event.time > self.time:
                self._record_network()

    def _record_network(self):
        """Records the state of the network at the current time."""
        self.network_history.record(self.time, self.state.network)

    def _record_crew_measures(self):
        """Records measures accumulated by crew members over the elapsed duration."""
        for element in self.state.network.elements:
            if not isinstance(element, SimCrewMember):
                continue
            location = element.location
            fraction = element.available_time_fraction
            self.crew_time_history.append(
                MoeCrewTime(
                    self.time,
                    location,
                    CREW_TIME_EXPLORATION,
                    self.duration * 24 * fraction,
                )
            )
            self.crew_time_history.append(
                MoeCrewTime(
                    self.time,
                    location,
                    CREW_TIME_UNAVAILABLE,
                    self.duration * 24 * (1 - fraction),
                )
            )
            if location is not None and location.is_exploration_site:
                self.crew_surface_days_history.append(
                    MoeCrewSurfaceDays(self.time, location, self.duration)
                )
                self.exploration_capability_history.append(
                    MoeExplorationCapability(
                        self.time,
                        location,
                        location.get_total_mass(ClassOfSupply.COS_6)
                        + location.get_total_mass(ClassOfSupply.COS_8),
                        self.duration,
                    )
                )

    def _record_transport_measures(self, event: TransportEvent):
        """Records measures of a transport which is about to be executed."""
        origin, destination = event.origin, event.destination
        if origin is None or destination is None:
            return
        elements = list({e.id: e for e in event.elements}.values())
        carriers = [e for e in elements if isinstance(e, SimCarrier)]
        if destination.is_exploration_site:
            self.exploration_mass_delivered_history.append(
                MoeExplorationMassDelivered(
                    self.time + event.duration,
                    destination,
                    sum(
                        e.get_total_mass(ClassOfSupply.COS_6)
                        + e.get_total_mass(ClassOfSupply.COS_8)
                        for e in elements
                    ),
                )
            )
        if isinstance(event, FlightTransportEvent):
            capacity = event.edge.max_cargo_mass
            amount = sum(c.total_mass for c in carriers)
        else:
            # NOTE: the reference implementation compares the total (rather
            # than cargo) mass of carriers to their cargo capacity
            capacity = sum(c.max_cargo_mass for c in carriers)
            amount = sum(c.cargo_mass for c in carriers)
        if origin.is_surface and origin.body == Body.EARTH:
            self.launch_mass_history.append(
                MoeLaunchMass(self.time, origin, sum(e.total_mass for e in elements))
            )
            self.up_mass_capacity_utilization_history.append(
                MoeMassCapacityUtilization(self.time, origin, amount, capacity)
            )
        elif destination.is_surface and destination.body == Body.EARTH:
            self.down_mass_capacity_utilization_history.append(
                MoeMassCapacityUtilization(self.time, destination, amount, capacity)
            )

    def _record_repair(self, mission, element, item, resource, amount):
        super()._record_repair(mission, element, item, resource, amount)
        repair_time = item.unit_mean_repair_time * amount
        self.crew_time_history.append(
            MoeCrewTime(
                mission.start_time,
                element.location,
                CREW_TIME_CORRECTIVE_MAINTENANCE,
                repair_time,
            )
        )
        self.crew_time_history.append(
            MoeCrewTime(
                mission.start_time,
                element.location,
                CREW_TIME_EXPLORATION,
                -repair_time,
            )
        )

    # ---------------------------------------------- measures of effectiveness

    @property
    def total_crew_surface_days(self) -> float:
        """The total crew surface days (crew-days)."""
        return sum(m.amount for m in self.crew_surface_days_history)

    @property
    def total_crew_time(self) -> float:
        """The total crew time (crew-hours)."""
        return sum(m.amount for m in self.crew_time_history)

    def get_total_crew_time(self, crew_time_type: str) -> float:
        """
        Gets the total crew time of one category.

        Args:
            crew_time_type (str): The crew time category.

        Returns:
            float: The total crew time (crew-hours).
        """
        return sum(m.amount for m in self.crew_time_history if m.type == crew_time_type)

    @property
    def total_exploration_capability(self) -> float:
        """The total exploration capability (kg-crew-days)."""
        return sum(m.duration * m.mass for m in self.exploration_capability_history)

    @property
    def total_exploration_mass_delivered(self) -> float:
        """The total exploration mass delivered (kg)."""
        return sum(m.amount for m in self.exploration_mass_delivered_history)

    @property
    def total_launch_mass(self) -> float:
        """The total mass (kg) launched from Earth."""
        return sum(m.amount for m in self.launch_mass_history)

    @staticmethod
    def _get_utilization(history: List[MoeMassCapacityUtilization]) -> float:
        capacity = sum(m.capacity for m in history)
        return sum(m.amount for m in history) / capacity if capacity > 0 else 0.0

    @property
    def total_up_mass_capacity_utilization(self) -> float:
        """The fraction of cargo mass capacity used by transports from Earth."""
        return self._get_utilization(self.up_mass_capacity_utilization_history)

    @property
    def total_down_mass_capacity_utilization(self) -> float:
        """The fraction of cargo mass capacity used by transports to Earth."""
        return self._get_utilization(self.down_mass_capacity_utilization_history)

    @property
    def total_relative_exploration_capability(self) -> float:
        """
        The exploration capability per launch mass relative to Apollo 17.
        """
        if self.total_launch_mass <= 0:
            return 0.0
        return (
            self.total_exploration_capability / APOLLO_17_EXPLORATION_CAPABILITY
        ) / (self.total_launch_mass / APOLLO_17_LAUNCH_MASS)
