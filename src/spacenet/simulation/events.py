"""
Events which change the simulation state.
"""

# pylint: disable=too-many-lines

import logging
import math
import sys
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from ..schemas import ClassOfSupply, StateType
from ..schemas.events.burn import BurnStage
from ..schemas.events.event import EventType
from .elements import (
    ElementContainer,
    OperationalState,
    SimCarrier,
    SimCrewMember,
    SimElement,
    SimPropulsiveVehicle,
    SimResourceContainer,
    SimResourceTank,
    SimSurfaceVehicle,
)
from .errors import SimDemand, SimSpatialError, SimWarning
from .network import SimBurn, SimEdge, SimLocation, SimNode
from .resources import Demand, DemandSet, SimResource

if TYPE_CHECKING:  # pragma: no cover
    from .mission import SimMission
    from .simulator import Simulator

logger = logging.getLogger(__name__)

#: Standard gravity (m/s^2) used in the rocket equation.
G0 = 9.81

#: Remaining change in velocity (m/s) below which a burn is considered complete.
DELTA_V_TOLERANCE = 1e-6

#: Seconds per day.
SECONDS_PER_DAY = 24 * 60 * 60

#: Priority assigned to events which shall execute after all other coincident events.
LAST_PRIORITY = sys.maxsize


def get_required_fuel_mass(stack_mass: float, delta_v: float, isp: float) -> float:
    """
    Gets the fuel mass required to achieve a change in velocity.

    Args:
        stack_mass (float): The initial mass (kg) of the stack including fuel.
        delta_v (float): The change in velocity (m/s).
        isp (float): The specific impulse (s).

    Returns:
        float: The required fuel mass (kg).
    """
    if isp <= 0:
        return stack_mass if delta_v > 0 else 0.0
    return stack_mass * (1 - math.exp(-delta_v / (isp * G0)))


def get_achieved_delta_v(stack_mass: float, isp: float, fuel_mass: float) -> float:
    """
    Gets the change in velocity achieved by burning a fuel mass.

    Args:
        stack_mass (float): The initial mass (kg) of the stack including fuel.
        isp (float): The specific impulse (s).
        fuel_mass (float): The mass (kg) of fuel burned.

    Returns:
        float: The change in velocity (m/s).
    """
    if isp <= 0 or fuel_mass <= 0 or stack_mass <= 0:
        return 0.0
    if fuel_mass >= stack_mass:
        return math.inf
    return isp * G0 * math.log(stack_mass / (stack_mass - fuel_mass))


def _sorted_elements(elements) -> List[SimElement]:
    """Lists unique elements in order (by name)."""
    unique = {}
    for element in elements:
        if element is not None:
            unique[element.id] = element
    return sorted(unique.values(), key=lambda e: e.sort_key)


def _names(elements) -> str:
    return "[" + ", ".join(str(e) for e in elements) + "]"


class SimEvent:
    """
    Base class for a simulation event.
    """

    event_type: Optional[EventType] = None
    #: Name assigned to events created without a name (default: the event type).
    default_name: Optional[str] = None

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        time: float = 0.0,
        priority: int = 0,
        location: Optional[SimLocation] = None,
        parent: Optional["SimEvent"] = None,
        mission_time: Optional[float] = None,
    ):
        if name is None:
            name = self.default_name
        if name is None:
            name = "Event" if self.event_type is None else self.event_type.value
        self.name = name
        #: Simulation time (days) relative to the scenario start. Until a
        #: mission event is scheduled, times are relative to the mission start.
        self.time = time if mission_time is None else mission_time
        #: Time (days) relative to the mission start (`None` for derived events).
        self.mission_time = mission_time
        #: Priority for coincident events (lower values execute first).
        self.priority = priority
        self.location = location
        #: Event which created this event, if any.
        self.parent = parent

    @property
    def root(self) -> "SimEvent":
        """The top-level event which (recursively) created this event."""
        return self if self.parent is None else self.parent.root

    def execute(self, simulator: "Simulator"):
        """
        Executes this event.

        Args:
            simulator (:obj:`Simulator`): The simulator.

        Raises:
            :obj:`SimError`: If the event cannot be executed.
        """
        raise NotImplementedError()

    def _log(self, message: str, *args):
        logger.info("%.3f: " + message, self.time, *args)

    def _warn(self, simulator: "Simulator", message: str):
        logger.warning("(%s) %s", self, message)
        simulator.warnings.append(SimWarning(simulator.time, self, message))

    def _check_location(self, simulator: "Simulator", element: SimElement):
        """Raises an error unless an element is at the location of this event."""
        if element.location is None:
            raise SimSpatialError(simulator.time, self, f"{element} was not found.")
        if element.location != self.location:
            raise SimSpatialError(
                simulator.time,
                self,
                f"{element} is located at {element.location} instead of {self.location}.",
            )

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"{type(self).__name__}({self.name!r}, time={self.time})"


class MissionEvent(SimEvent):
    """
    Event which schedules the events of a mission at the mission start.
    """

    def __init__(self, mission: "SimMission", **kwargs):
        kwargs.setdefault("name", mission.name)
        kwargs.setdefault("time", mission.start_time)
        kwargs.setdefault("location", mission.origin)
        super().__init__(**kwargs)
        self.mission = mission

    def execute(self, simulator: "Simulator"):
        if not self.mission.events:
            self._warn(simulator, "No events defined.")
        self._log("Commencing Mission: %s", self.mission.name)
        for event in self.mission.events:
            event.time = (
                simulator.settings.round_time(event.mission_time or 0.0) + self.time
            )
            simulator.schedule(event)


class CreateEvent(SimEvent):
    """
    Event which creates elements inside a location or carrier.
    """

    event_type = EventType.CREATE_ELEMENTS

    def __init__(
        self,
        *,
        elements: Optional[List[SimElement]] = None,
        container: Optional[ElementContainer] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.elements: List[SimElement] = list(elements) if elements is not None else []
        self.container = container

    def execute(self, simulator: "Simulator"):
        if self.container is None:
            self._warn(
                simulator, f"No container defined, defaulting to {self.location}."
            )
            self.container = self.location
        if isinstance(self.container, SimCarrier) and self.container.location is None:
            raise SimSpatialError(
                simulator.time, self, f"{self.container} was not found."
            )
        elements = _sorted_elements(self.elements)
        if not elements:
            self._warn(simulator, "No elements defined.")
        self._log("Creating %s in %s", _names(elements), self.container)
        for element in elements:
            if element.location is not None:
                raise SimSpatialError(
                    simulator.time,
                    self,
                    f"{element} already exists at {element.location}.",
                )
            if self.container.add(element):
                simulator.state.network.register(element)
            else:
                raise SimSpatialError(
                    simulator.time,
                    self,
                    f"{element} could not be added to {self.container}.",
                )


class MoveEvent(SimEvent):
    """
    Event which moves elements to a location or carrier.
    """

    event_type = EventType.MOVE_ELEMENTS

    def __init__(
        self,
        *,
        elements: Optional[List[SimElement]] = None,
        container: Optional[ElementContainer] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        # the list is intentionally not copied: transports share one list of
        # elements with their burn events so staged elements are not moved
        self.elements: List[SimElement] = elements if elements is not None else []
        self.container = container

    def execute(self, simulator: "Simulator"):
        if self.container is None:
            self._warn(
                simulator, f"No container defined, defaulting to {self.location}."
            )
            self.container = self.location
        if isinstance(self.container, SimCarrier) and self.container.location is None:
            raise SimSpatialError(
                simulator.time, self, f"{self.container} was not found."
            )
        elements = _sorted_elements(self.elements)
        if not elements:
            self._warn(simulator, "No elements defined.")
            return
        self._log("Transferring %s to %s", _names(elements), self.container)
        for element in elements:
            self._check_location(simulator, element)
            if not self.container.add(element):
                raise SimSpatialError(
                    simulator.time,
                    self,
                    f"{element} could not be added to {self.container}.",
                )


class RemoveEvent(SimEvent):
    """
    Event which removes elements from the simulation.
    """

    event_type = EventType.REMOVE_ELEMENTS

    def __init__(self, *, elements: Optional[List[SimElement]] = None, **kwargs):
        super().__init__(**kwargs)
        self.elements: List[SimElement] = list(elements) if elements is not None else []

    def execute(self, simulator: "Simulator"):
        elements = _sorted_elements(self.elements)
        if not elements:
            self._warn(simulator, "No elements defined.")
            return
        for element in elements:
            self._check_location(simulator, element)
            self._log("Removing %s from Simulation", element)
            element.container.remove(element)
            simulator.state.network.unregister(element)


class AddEvent(SimEvent):
    """
    Event which adds resources to a resource container.
    """

    event_type = EventType.ADD_RESOURCES

    def __init__(
        self,
        *,
        demands: Optional[DemandSet] = None,
        container: Optional[SimElement] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.demands = demands if demands is not None else DemandSet()
        self.container = container

    def execute(self, simulator: "Simulator"):
        container = _get_resource_container(simulator, self, self.container)
        self._check_location(simulator, container)
        if len(self.demands) == 0:
            self._warn(simulator, "No demands defined.")
            return
        self._log("Adding %s to %s", self.demands, container)
        for demand in self.demands:
            if not container.add(demand.resource, demand.amount):
                raise SimSpatialError(
                    simulator.time, self, f"{demand} could not be added to {container}."
                )


class TransferEvent(SimEvent):
    """
    Event which transfers resources between two resource containers.
    """

    event_type = EventType.TRANSFER_RESOURCES

    def __init__(
        self,
        *,
        demands: Optional[DemandSet] = None,
        origin_container: Optional[SimElement] = None,
        destination_container: Optional[SimElement] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.demands = demands if demands is not None else DemandSet()
        self.origin_container = origin_container
        self.destination_container = destination_container

    def execute(self, simulator: "Simulator"):
        origin = _get_resource_container(simulator, self, self.origin_container)
        destination = _get_resource_container(
            simulator, self, self.destination_container
        )
        if destination.location is None:
            raise SimSpatialError(simulator.time, self, f"{destination} was not found.")
        if origin.location is None:
            raise SimSpatialError(simulator.time, self, f"{origin} was not found.")
        if origin.location != destination.location:
            raise SimSpatialError(
                simulator.time,
                self,
                f"{destination} is located at {destination.location} "
                f"instead of {origin.location}.",
            )
        if len(self.demands) == 0:
            self._warn(simulator, "No demands defined.")
            return
        self._log("Transferring %s to %s", self.demands, destination)
        for demand in self.demands:
            if not origin.remove(demand.resource, demand.amount):
                raise SimSpatialError(
                    simulator.time,
                    self,
                    f"{demand} could not be removed from {origin}.",
                )
            if not destination.add(demand.resource, demand.amount):
                origin.add(demand.resource, demand.amount)
                raise SimSpatialError(
                    simulator.time,
                    self,
                    f"{demand} could not be added to {destination}.",
                )


def _get_resource_container(simulator: "Simulator", event: SimEvent, element):
    """
    Gets the resource container of an element. Vehicles are represented by
    their integral fuel tank.
    """
    if element is None:
        raise SimSpatialError(simulator.time, event, "No resource container defined.")
    if isinstance(element, (SimResourceContainer, SimResourceTank)):
        return element
    fuel_tank = getattr(element, "fuel_tank", None)
    if fuel_tank is not None:
        return fuel_tank
    raise SimSpatialError(
        simulator.time, event, f"{element} is not a resource container."
    )


class DemandEvent(SimEvent):
    """
    Event which demands (consumes or produces) resources. Demands which can
    not be satisfied with available resources are raised as an error.
    """

    event_type = EventType.CONSUME_RESOURCES
    default_name = "Demand Resources"

    def __init__(
        self,
        *,
        element: Optional[SimElement] = None,
        demands: Optional[DemandSet] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.element = element
        self.demands = demands if demands is not None else DemandSet()

    def execute(self, simulator: "Simulator"):
        if self.location is None:
            raise SimSpatialError(simulator.time, self, "Mission location.")
        if self.element is not None:
            self._check_location(simulator, self.element)
        demands = DemandSet(d for d in self.demands if abs(d.amount) > 0)
        self._log(
            "Demand for %s from %s",
            self.demands,
            self.location if self.element is None else self.element,
        )
        if simulator.demands_satisfied:
            if self.element is not None:
                self.element.satisfy_demands(demands, simulator)
                if isinstance(self.element.container, SimCarrier):
                    self.element.container.satisfy_demands(demands, simulator)
            for element in self.location.contents:
                element.satisfy_demands(demands, simulator)
        if abs(demands.total_mass) > 0:
            if demands.total_mass > 0 and simulator.packing_demands_added:
                packing_amount = 0.0
                for demand in demands:
                    if demand.mass > 0 and demand.resource.packing_factor > 0:
                        packing_amount += demand.amount * demand.resource.packing_factor
                demands.add(
                    Demand(
                        SimResource.generic(simulator.settings, ClassOfSupply.COS_5),
                        packing_amount,
                    )
                )
            raise SimDemand(simulator.time, self, self.location, self.element, demands)


class ReconfigureEvent(SimEvent):
    """
    Event which changes the operational state of one element.
    """

    event_type = EventType.RECONFIGURE_ELEMENT

    def __init__(
        self,
        *,
        element: Optional[SimElement] = None,
        state: Optional[OperationalState] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.element = element
        self.state = state

    def execute(self, simulator: "Simulator"):
        if self.element is None:
            self._warn(simulator, "No element defined.")
            return
        self._check_location(simulator, self.element)
        if not self.element.set_current_state(self.state):
            raise SimSpatialError(
                simulator.time,
                self,
                f"Element {self.element} does not contain state {self.state}.",
            )
        self._log("Reconfiguring %s to %s state", self.element, self.state)


class ReconfigureGroupEvent(SimEvent):
    """
    Event which changes several elements to their first state of a given type.
    """

    event_type = EventType.RECONFIGURE_ELEMENTS
    default_name = "Reconfigure Group"

    def __init__(
        self,
        *,
        elements: Optional[List[SimElement]] = None,
        state_type: StateType = StateType.ACTIVE,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.elements: List[SimElement] = list(elements) if elements is not None else []
        self.state_type = StateType(state_type)

    def execute(self, simulator: "Simulator"):
        elements = _sorted_elements(self.elements)
        if not elements:
            self._warn(simulator, "No elements defined.")
            return
        for element in elements:
            state = next(
                (s for s in element.states if s.state_type == self.state_type), None
            )
            self._check_location(simulator, element)
            if state is None:
                self._warn(
                    simulator, f"No {self.state_type.value} state for {element}."
                )
            elif element.set_current_state(state):
                self._log("Reconfiguring %s to %s state", element, state)
            else:
                raise SimSpatialError(
                    simulator.time,
                    self,
                    f"Element {element} does not contain state {state}.",
                )


class BurnEvent(SimEvent):
    """
    Event for an impulsive burn composed of a sequence of burn (fire engine)
    and stage (discard element) actions.
    """

    event_type = EventType.PROPULSIVE_BURN

    def __init__(
        self,
        *,
        elements: Optional[List[SimElement]] = None,
        burn: Optional[SimBurn] = None,
        burn_stage_sequence: Optional[List[Tuple[BurnStage, SimElement]]] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        # the list is intentionally not copied (see `MoveEvent`)
        self.elements: List[SimElement] = elements if elements is not None else []
        self.burn = burn if burn is not None else SimBurn()
        #: Sequence of (action, element) pairs.
        self.burn_stage_sequence: List[Tuple[BurnStage, SimElement]] = (
            list(burn_stage_sequence) if burn_stage_sequence is not None else []
        )

    def execute(self, simulator: "Simulator"):
        delta_v_required = self.burn.delta_v
        priority = -LAST_PRIORITY
        for action, element in self.burn_stage_sequence:
            if BurnStage(action) == BurnStage.BURN:
                delta_v_required = self._burn(simulator, element, delta_v_required)
            else:
                stage = RemoveEvent(
                    time=self.time,
                    priority=priority,
                    parent=self,
                    location=self.location,
                    elements=[element],
                )
                priority += 1
                stage.execute(simulator)
                self.elements[:] = [e for e in self.elements if e is not element]
        if delta_v_required > DELTA_V_TOLERANCE:
            raise SimSpatialError(
                simulator.time,
                self,
                "Insufficient delta-v achieved, - remaining delta-v: "
                f"{delta_v_required:.1f} m/s.",
            )

    def _burn(
        self, simulator: "Simulator", vehicle: SimElement, delta_v: float
    ) -> float:
        """Burns fuel from a vehicle and returns the remaining required delta-v."""
        if not isinstance(vehicle, SimPropulsiveVehicle):
            raise SimSpatialError(
                simulator.time, self, f"{vehicle} is not a propulsive vehicle."
            )
        tank = vehicle.fuel_tank
        unit_mass = 1.0 if tank.resource is None else tank.resource.unit_mass
        stack_mass = sum(e.total_mass for e in _sorted_elements(self.elements))
        self._log("Starting %s Burn for target %.2f m/s delta-V", vehicle, delta_v)
        if vehicle.isp <= 0:
            self._warn(simulator, f"{vehicle} has no specific impulse defined.")
            return delta_v
        # NOTE: the reference implementation compares fuel mass (kg) to the
        # tank amount (units) which is only valid for a unit mass of 1 kg
        required_fuel = (
            get_required_fuel_mass(stack_mass, delta_v, vehicle.isp) / unit_mass
        )
        if required_fuel > tank.amount:
            achieved = get_achieved_delta_v(
                stack_mass, vehicle.isp, tank.amount * unit_mass
            )
            delta_v -= achieved
            tank.amount = 0.0
            self._log(
                "%s Burn achieved %.2f m/s delta-V, %.2f m/s delta-V remaining",
                vehicle,
                achieved,
                delta_v,
            )
            return delta_v
        tank.remove(tank.resource, required_fuel)
        self._log(
            "%s Burn achieved %.2f m/s delta-V, %.2f kg fuel remaining",
            vehicle,
            delta_v,
            tank.cargo_mass,
        )
        return 0.0


class _CrewActivityEvent(SimEvent):
    """
    Base class for events in which crew members leave a crew vehicle.
    """

    # pylint: disable=abstract-method

    def __init__(
        self,
        *,
        vehicle: Optional[SimCarrier] = None,
        eva_duration: float = 8.0,
        state_map: Optional[Dict[SimElement, Optional[OperationalState]]] = None,
        demands: Optional[DemandSet] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.vehicle = vehicle
        #: Duration (hours) of the extra-vehicular activity.
        self.eva_duration = eva_duration
        #: State during the activity for each participating element (`None` for no change).
        self.state_map: Dict[SimElement, Optional[OperationalState]] = (
            state_map if state_map is not None else {}
        )
        self.demands = demands if demands is not None else DemandSet()

    def _check(self, simulator: "Simulator"):
        if not self.state_map:
            self._warn(simulator, "No crew members defined.")
        if self.vehicle is None:
            raise SimSpatialError(simulator.time, self, "No crew habitat defined.")
        self._check_location(simulator, self.vehicle)
        for member in _sorted_elements(self.state_map):
            self._check_location(simulator, member)


class EvaEvent(_CrewActivityEvent):
    """
    Event for an extra-vehicular activity during which crew members leave a
    crew vehicle and optionally change operational state.
    """

    event_type = EventType.CREWED_EVA

    def execute(self, simulator: "Simulator"):
        self._check(simulator)
        self._log("Commencing EVA at %s for %s hours", self.location, self.eva_duration)
        if not simulator.settings.detailed_eva:
            return
        members = _sorted_elements(self.state_map)
        end_time = self.time + self.eva_duration / 24
        previous_states = {}
        for member in members:
            if self.state_map[member] is not None:
                previous_states[member] = member.current_state
                simulator.schedule(
                    ReconfigureEvent(
                        time=self.time,
                        priority=self.priority,
                        parent=self,
                        location=self.location,
                        element=member,
                        state=self.state_map[member],
                    )
                )
        simulator.schedule(
            MoveEvent(
                time=self.time,
                priority=self.priority,
                parent=self,
                location=self.location,
                container=self.location,
                elements=list(members),
            )
        )
        simulator.schedule(
            MoveEvent(
                time=end_time,
                parent=self,
                location=self.location,
                container=self.vehicle,
                elements=list(members),
            )
        )
        for member in members:
            if previous_states.get(member) is not None:
                simulator.schedule(
                    ReconfigureEvent(
                        time=end_time,
                        parent=self,
                        location=self.location,
                        element=member,
                        state=previous_states[member],
                    )
                )
        if len(self.demands) > 0:
            simulator.schedule(
                DemandEvent(
                    time=end_time,
                    parent=self,
                    location=self.location,
                    element=self.vehicle,
                    demands=self.demands,
                )
            )


class ExplorationProcess(_CrewActivityEvent):
    """
    Event for an exploration period with regularly-scheduled extra-vehicular activities.
    """

    event_type = EventType.CREWED_EXPLORATION

    def __init__(self, *, duration: float = 0.0, eva_per_week: float = 0.0, **kwargs):
        super().__init__(**kwargs)
        #: Duration (days) of the exploration.
        self.duration = duration
        #: Number of extra-vehicular activities per week.
        self.eva_per_week = eva_per_week

    @property
    def number_eva(self) -> int:
        """The number of extra-vehicular activities during the exploration."""
        return int(math.floor(self.duration * self.eva_per_week / 7))

    @property
    def hours_between_eva(self) -> float:
        """The time (hours) between successive extra-vehicular activities."""
        return (self.duration * 24 - self.eva_duration * self.number_eva) / (
            self.number_eva + 1
        )

    def execute(self, simulator: "Simulator"):
        self._check(simulator)
        self._log(
            "Commencing exploration at %s for %s days with %d EVAs",
            self.location,
            self.duration,
            self.number_eva,
        )
        # NOTE: the reference implementation checks the detailed EVA option here
        if not simulator.settings.detailed_exploration:
            return
        for i in range(self.number_eva):
            simulator.schedule(
                EvaEvent(
                    time=self.time + (i + 1) * self.hours_between_eva / 24,
                    parent=self,
                    location=self.location,
                    eva_duration=self.eva_duration,
                    vehicle=self.vehicle,
                    state_map=self.state_map,
                    demands=self.demands,
                )
            )


class TransportEvent(SimEvent):
    """
    Base class for an event which transports elements along an edge.
    """

    def __init__(self, *, edge: Optional[SimEdge] = None, **kwargs):
        super().__init__(**kwargs)
        self.edge = edge

    @property
    def elements(self) -> List[SimElement]:
        """The transported (top-level) elements."""
        raise NotImplementedError()

    @property
    def duration(self) -> float:
        """The duration (days) of the transport."""
        return 0.0 if self.edge is None else self.edge.duration

    @property
    def origin(self) -> Optional[SimNode]:
        """The node at which the transport starts."""
        return None if self.edge is None else self.edge.origin

    @property
    def destination(self) -> Optional[SimNode]:
        """The node at which the transport ends."""
        return None if self.edge is None else self.edge.destination

    def _check_edge(self, simulator: "Simulator", label: str):
        if self.edge is None:
            raise SimSpatialError(simulator.time, self, f"No {label} edge defined.")


class FlightTransportEvent(TransportEvent):
    """
    Event which transports elements along a flight edge with known capacity.
    """

    event_type = EventType.FLIGHT_TRANSPORT

    def __init__(self, *, elements: Optional[List[SimElement]] = None, **kwargs):
        super().__init__(**kwargs)
        self._elements: List[SimElement] = (
            list(elements) if elements is not None else []
        )

    @property
    def elements(self) -> List[SimElement]:
        return self._elements

    def execute(self, simulator: "Simulator"):
        elements = _sorted_elements(self._elements)
        if not elements:
            self._warn(simulator, "No elements defined.")
        self._check_edge(simulator, "flight")
        mass = 0.0
        crew = 0
        for element in elements:
            self._check_location(simulator, element)
            mass += element.total_mass
            # NOTE: the reference implementation only counts crew directly
            # inside the transported carriers
            if isinstance(element, SimCrewMember):
                crew += 1
            elif isinstance(element, SimCarrier):
                crew += element.total_crew_size
        if mass > self.edge.max_cargo_mass:
            raise SimSpatialError(
                simulator.time,
                self,
                "Flight cargo mass over capacity: "
                f"{mass:.1f}/{self.edge.max_cargo_mass:.1f} kg",
            )
        if crew > self.edge.max_crew_size:
            raise SimSpatialError(
                simulator.time,
                self,
                f"Flight crew size over capacity: {crew}/{self.edge.max_crew_size}",
            )
        self._log("Commencing flight")
        MoveEvent(
            time=self.time,
            priority=self.priority,
            parent=self,
            location=self.edge.origin,
            container=self.edge,
            elements=elements,
        ).execute(simulator)
        simulator.schedule(
            MoveEvent(
                time=self.time + self.edge.duration,
                parent=self,
                location=self.edge,
                container=self.edge.destination,
                elements=elements,
            )
        )


class SpaceTransportEvent(TransportEvent):
    """
    Event which transports elements along a space edge using a sequence of burns.
    """

    event_type = EventType.SPACE_TRANSPORT

    def __init__(
        self,
        *,
        elements: Optional[List[SimElement]] = None,
        burn_stage_sequence: Optional[List[List[Tuple[BurnStage, SimElement]]]] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._elements: List[SimElement] = (
            list(elements) if elements is not None else []
        )
        #: Sequence of (action, element) pairs for each burn of the edge.
        self.burn_stage_sequence: List[List[Tuple[BurnStage, SimElement]]] = (
            list(burn_stage_sequence) if burn_stage_sequence is not None else []
        )

    @property
    def elements(self) -> List[SimElement]:
        return self._elements

    def execute(self, simulator: "Simulator"):
        # one list is shared by the derived events so that elements staged
        # during a burn are excluded from subsequent burns and the arrival
        elements = _sorted_elements(self._elements)
        if not elements:
            self._warn(simulator, "No elements defined.")
        self._check_edge(simulator, "space")
        for element in elements:
            self._check_location(simulator, element)
        self._log("Commencing space transport")
        MoveEvent(
            time=self.time,
            priority=self.priority,
            parent=self,
            location=self.edge.origin,
            container=self.edge,
            elements=elements,
        ).execute(simulator)
        number_burns = len(self.edge.burns)
        for i, burn in enumerate(self.edge.burns):
            simulator.schedule(
                BurnEvent(
                    time=self.time + burn.time,
                    priority=i - number_burns,
                    parent=self,
                    location=self.edge,
                    elements=elements,
                    burn=burn,
                    burn_stage_sequence=(
                        self.burn_stage_sequence[i]
                        if i < len(self.burn_stage_sequence)
                        else []
                    ),
                )
            )
        simulator.schedule(
            MoveEvent(
                time=self.time + self.edge.duration,
                parent=self,
                location=self.edge,
                container=self.edge.destination,
                elements=elements,
            )
        )


class SurfaceTransportEvent(TransportEvent):
    """
    Event which transports a surface vehicle along a surface edge.
    """

    event_type = EventType.SURFACE_TRANSPORT

    def __init__(
        self,
        *,
        vehicle: Optional[SimSurfaceVehicle] = None,
        transport_state: Optional[OperationalState] = None,
        speed: float = 0.0,
        duty_cycle: float = 1.0,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.vehicle = vehicle
        #: State of the vehicle during the transport (`None` for no change).
        self.transport_state = transport_state
        #: Transport speed (m/s).
        self.speed = speed
        #: Fraction of time the vehicle moves at the transport speed.
        self.duty_cycle = 1.0 if duty_cycle is None else duty_cycle

    @property
    def elements(self) -> List[SimElement]:
        return [] if self.vehicle is None else [self.vehicle]

    @property
    def is_reversed(self) -> bool:
        """True, if the edge is traversed from its destination to its origin."""
        return self.edge is not None and self.location == self.edge.destination

    @property
    def origin(self) -> Optional[SimNode]:
        if self.edge is None:
            return None
        return self.edge.destination if self.is_reversed else self.edge.origin

    @property
    def destination(self) -> Optional[SimNode]:
        if self.edge is None:
            return None
        return self.edge.origin if self.is_reversed else self.edge.destination

    @property
    def duration(self) -> float:
        # NOTE: uses the units of the object schemas (distance in meters and
        # speed in meters per second); the reference implementation divides
        # distance by (speed * duty cycle * 24), i.e., kilometers and
        # kilometers per hour
        if self.edge is None or self.speed <= 0 or self.duty_cycle <= 0:
            return math.inf
        return self.edge.distance / (self.speed * self.duty_cycle * SECONDS_PER_DAY)

    def execute(self, simulator: "Simulator"):
        self._check_edge(simulator, "surface")
        if self.vehicle is None:
            raise SimSpatialError(simulator.time, self, "No surface vehicle defined.")
        self._check_location(simulator, self.vehicle)
        if self.speed <= 0 or self.duty_cycle <= 0:
            raise SimSpatialError(simulator.time, self, "Infinite travel duration.")
        self._log("Commencing surface transport")
        duration = simulator.settings.round_time(self.duration)
        previous_state = self.vehicle.current_state
        if self.transport_state is not None:
            ReconfigureEvent(
                time=self.time,
                priority=self.priority,
                parent=self,
                location=self.origin,
                element=self.vehicle,
                state=self.transport_state,
            ).execute(simulator)
        MoveEvent(
            time=self.time,
            priority=self.priority,
            parent=self,
            location=self.location,
            container=self.edge,
            elements=[self.vehicle],
        ).execute(simulator)
        simulator.schedule(
            MoveEvent(
                time=self.time + duration,
                priority=-1,
                parent=self,
                location=self.edge,
                container=self.destination,
                elements=[self.vehicle],
            )
        )
        if previous_state is not None:
            simulator.schedule(
                ReconfigureEvent(
                    time=self.time + duration,
                    priority=0,
                    parent=self,
                    location=self.destination,
                    element=self.vehicle,
                    state=previous_state,
                )
            )
