# Simulators have networks and event queues, they take from the event queue, which is sorted
# by time, and re-populate the event queue with new generated events.

# You can model a time-expanded graph in a memory-efficient way by having the contents be the
# time-expanded part.
from abc import ABC, abstractmethod
from datetime import datetime
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Set,
    Tuple,
    TypeVar,
    Union,
)
from uuid import UUID

from pydantic import BaseModel, Field

from spacenet.analysis.min_heap import MinHeap
from spacenet.schemas import (
    Burn,
    ElementCarrier,
    Event,
    PropulsiveBurn,
    PropulsiveVehicle,
    Scenario,
    AllUUIDEdges,
    AllNodes,
    AllElements,
    MoveElements,
    MakeElements,
    RemoveElements,
)
from .decompose_events import decompose_event
from .simulation_errors import SimError
from .exceptions import *

from spacenet.fuel_formulas.functions import *

__all__ = ["Simulation", "SimResult", "SimError"]


class ContainsElements(BaseModel):
    contents: List["SimElement"] = Field(default_factory=list)


class SimElement(ContainsElements):
    """
    An element under simulation; wraps Element schema.
    """

    inner: AllElements
    # TODO: should not be able to carry self, even recursively: create Contains Graph and BFS
    #  it from one element to itself, assert that only path is zero-length

    def __hash__(self):
        return hash(self.inner)

    def total_mass(self) -> Tuple[float, List["SimError"]]:
        total_mass = self.inner.mass
        errors = []
        visited = {self}
        stack = list(self.contents)
        # Iteratively depth-first search throughout this connected component of the containment
        # graph, totalling the mass along the way.
        while stack:
            next_element = stack.pop()
            total_mass += next_element.inner.mass
            for e in next_element.contents:
                # TODO: this is a pretty suboptimal solution at the moment. We only check that
                #  self is not contained in a cycle, which does not guarantee a cycle doesn't
                #  exist more generally.
                if e == self:
                    errors.append(
                        SimError(
                            description=f"Element {self.inner.name} cannot contain itself"
                        )
                    )
                elif e in visited:
                    errors.append(
                        SimError(
                            description=f"Element {e.inner.name} has multiple containers"
                        )
                    )
                else:
                    stack.append(e)
            visited.add(next_element)
        return total_mass, errors


ContainsElements.update_forward_refs()


class SimNode(ContainsElements):
    """
    A node under simulation; wraps Node schema.
    """

    inner: AllNodes

    def __hash__(self):
        # This is safe because, assuming Node is safe to hash, we don't hash the mutable
        # state in contents
        return hash(self.inner)


class SimEdge(ContainsElements):
    """
    An edge under simulation; wraps Edge schema.
    """

    inner: AllUUIDEdges

    def __hash__(self):
        # Analogous safety argument as to SimNode
        return hash(self.inner)


SimElement.update_forward_refs()


class SimResult(BaseModel):
    """
    A type representing the result of a simulation.
    """

    nodes: List[SimNode]
    edges: List[SimEdge]
    end_time: datetime
    namespace: Dict[UUID, Union[SimElement, SimNode, SimEdge]]


class SimEvent(BaseModel, ABC):
    """
    An event in simulation.
    """

    timestamp: datetime
    priority: int

    def __lt__(self, other: "SimEvent") -> bool:
        return (self.timestamp, self.priority) < (other.timestamp, other.priority)

    @abstractmethod
    def validate_ids_exist(self, sim: "Simulation") -> None:
        """
        Validate this event, checking that its referenced values are present
        in the namespace of the provided simulation.

        :param sim: event to validate
        :raise UnrecognizedID: if this event has referenced values not present
        in the namespace
        """
        pass

    @abstractmethod
    def process_with_ctx(self, sim: "Simulation") -> None:
        """
        Process this event given the context of ``sim``, modifying ``sim``.

        :param sim:  simulation the event occurs in
        """
        pass


class Move(SimEvent):
    """
    Represents an event moving elements, one of the four primitive SimEvents.
    """

    event: MoveElements

    def validate_ids_exist(self, sim: "Simulation") -> None:
        event = self.event
        if not sim._id_exists(event.origin_id):
            raise UnrecognizedID(f"Origin id {event.origin_id} does not exist")
        elif not sim._id_exists(event.destination_id):
            raise UnrecognizedID(
                f"Destination id {event.destination_id} does not exist"
            )
        for id_ in event.to_move:
            if not sim._id_exists(id_):
                raise UnrecognizedID(f"ID {id_} does not exist")

    def process_with_ctx(self, sim: "Simulation") -> None:
        # Move all elements in the list to the new destination
        # Possible errors:
        #   source is not a container -> error for each moved element
        #   destination is not a container -> error for each moved element
        #   some element in the list is not actually an element
        prev_error_count = len(sim.errors)
        source = self.event.origin_id
        sim._add_errors(
            _id_exists_and_is_container(id_=source, timestamp=self.timestamp, sim=sim)
        )
        dest = self.event.destination_id
        sim._add_errors(
            _id_exists_and_is_container(id_=dest, timestamp=self.timestamp, sim=sim)
        )
        sim._add_errors(_all_ids_are_elements(self.event.to_move, self.timestamp, sim))
        # Filter source contents and move them over
        prev_contents = sim.namespace[source].contents
        to_move_set: Set[SimElement] = set(sim.namespace[id_] for id_ in self.event.to_move)
        new_contents = [
            element for element in prev_contents if element not in to_move_set
        ]
        # TODO: maintain invariant that elements don't contain themselves or have
        #  multiple containers
        sim.namespace[source].contents = new_contents
        sim.namespace[dest].contents.extend(
            to_move_set
        )


class Create(SimEvent):
    """
    Represents an event creating elements, one of the four primitive SimEvents.
    """

    event: MakeElements

    def validate_ids_exist(self, sim: "Simulation") -> None:
        event = self.event
        if not sim._id_exists(event.entry_point_id):
            raise UnrecognizedID(f"Entry point {event.entry_point_id} does not exist")
        for id_ in event.elements:
            if not sim._id_exists(id_):
                raise UnrecognizedID(f"ID {id_} does not exist")

    def process_with_ctx(self, sim: "Simulation") -> None:
        # Create all elements in the list at the specified location
        # Possible errors:
        #   location is not a container -> error for each created element
        #   values in the list don't correspond to actual elements
        entry_point = self.event.entry_point_id
        sim._add_errors(
            _id_exists_and_is_container(
                id_=entry_point, timestamp=self.timestamp, sim=sim
            )
        )
        sim._add_errors(
            _all_ids_are_elements(
                ids=self.event.elements, timestamp=self.timestamp, sim=sim
            )
        )
        sim.namespace[entry_point].contents.extend(
            sim.namespace[id_] for id_ in self.event.elements
        )


class Remove(SimEvent):
    """
    Represents an event removing elements, one of the four primitive SimEvents.
    """

    event: RemoveElements

    def validate_ids_exist(self, sim: "Simulation") -> None:
        event = self.event
        if not sim._id_exists(event.removal_point_id):
            raise UnrecognizedID(
                f"Removal point {event.removal_point_id} does not exist"
            )
        for id_ in event.elements:
            if not sim._id_exists(id_):
                raise UnrecognizedID(f"ID {id_} does not exist")

    def process_with_ctx(self, sim: "Simulation") -> None:
        # Remove all elements in the list at the specified location
        # Possible errors:
        #   location is not a container -> error for each created element
        #   values in the list don't correspond to actual elements
        #   elements provided aren't actually at the specified location
        removal_point_id = self.event.removal_point_id
        sim._add_errors(
            _id_exists_and_is_container(
                id_=self.event.removal_point_id, timestamp=self.timestamp, sim=sim
            )
        )
        sim._add_errors(
            _all_ids_are_elements_at_location(
                ids=self.event.elements,
                location=removal_point_id,
                timestamp=self.timestamp,
                sim=sim,
            )
        )
        prev_contents = sim.namespace[removal_point_id].contents
        elements_to_remove = set(self.event.elements)
        new_contents = [
            element for element in prev_contents if element not in elements_to_remove
        ]
        sim.namespace[removal_point_id].contents = new_contents


class BurnEvent(SimEvent):
    """
    Represents a burn, one of the four primitive SimEvents.
    """

    event: Burn
    elements: List[UUID]  # ordered: last element is first to have delta-v consumed

    def validate_ids_exist(self, sim: "Simulation") -> None:
        raise NotImplementedError

    def process_with_ctx(self, sim: "Simulation") -> None:
        # TODO
        # Consume the fuel at the given elements until enough fuel has been consumed
        # to satisfy delta-v requirement
        # Possible errors:
        #   values in the list don't correspond to actual elements
        #   not enough fuel (if this is a problem depends, but it's probably more efficient to
        #    just not add burn events if there's no fuel constraint and just stage)
        raise NotImplementedError

        # delta_ve = event.delta_v
        # for element in elements:
        # init_mass = element.mass
        # fin_mass = final_mass_from(delta_v: delta_ve, isp: 0, m_0: init_mass)
        # req_deltav = delts_v_from(isp: 0, m_0: init_mass, m_f: fin_mass)
        # if (req_deltav > delta_ve):
        # subtract mass/fuel
        # else:
        # delta_ve -= req_deltav
        # RemoveElement? stage


T = TypeVar("T")
SimCallback = Callable[["Simulation", Optional[T]], T]
SimEntity = Union[SimEdge, SimElement, SimNode]

EVENT_TO_SIM_EVENT = {MakeElements: Create, MoveElements: Move, RemoveElements: Remove}


class Simulation:
    """
    Represents a campaign simulation.
    """

    __slots__ = (
        "network",
        "event_queue",
        "errors",
        "pre_listeners",
        "post_listeners",
        "namespace",
        "current_time",
    )

    def __init__(
        self,
        scenario: Scenario,
        pre_listeners: Optional[Dict[SimCallback[Any], Any]] = None,
        post_listeners: Optional[Dict[SimCallback[Any], Any]] = None,
        propulsive: bool = False,
    ) -> None:
        """
        Construct a new simulation, raising errors if the provided scenario cannot be run
        without raising an exception.

        :param scenario: scenario defining network and events to simulate
        :param pre_listeners: listeners to run before each event
        :param post_listeners: listeners to run after each event
        :raise EventDateOverflowError: if the time an event ends, relative to mission start,
            cannot be represented as a timedelta, or the absolute time an event occurs cannot
            be represented as a datetime
        :raise UnrecognizedID: if an event references an ID that does not exist in the
            namespace
        :raise UnrecognizedEdgeEndpoint: if an edge has an endpoint which is not a network node
        """
        self.namespace: Dict[UUID, SimEntity] = {}
        for id_, node in scenario.network.nodes.items():
            self.namespace[id_] = SimNode(inner=node)
        for id_, edge in scenario.network.edges.items():
            self.namespace[id_] = SimEdge(inner=edge)
        for id_, element in scenario.elementList.items():
            self.namespace[id_] = SimElement(inner=element)
        assert len(scenario.network.nodes) + len(scenario.network.edges) + len(
            scenario.elementList
        ) == len(self.namespace), "expected no duplicate IDs"
        self.network: Dict[
            SimNode, Set[SimEdge]
        ] = {}  # adjacency list graph representation
        for id_ in scenario.network.nodes:
            node = self.namespace[id_]
            self.network.setdefault(node, set())
        for id_ in scenario.network.edges:
            edge = self.namespace[id_]
            for endpoint in (edge.inner.origin_id, edge.inner.destination_id):
                if endpoint not in scenario.network.nodes:
                    raise UnrecognizedEdgeEndpoint(
                        f"Edge {id_} has an endpoint {endpoint} not found in network"
                    )
            src = self.namespace[edge.inner.origin_id]
            self.network[src].add(edge)
            # add edges to adj-list rep
        events = [
            atomic_event
            for mission in scenario.missionList
            for event in mission.events
            for atomic_event in Simulation._decompose_event(event, mission.start_date)
        ]
        # TODO: can make a helper fn to figure out if should include the element and filter in
        #  comprehension
        if not propulsive:
            events = [e for e in events if not isinstance(e, BurnEvent)]
        self.event_queue: MinHeap[SimEvent] = MinHeap(events)
        self.errors: List[SimError] = []
        # Type annotations below aren't tight: Dict is a mapping of SimCallback[T] to T, but
        # different T can be contained in the same dict
        self.pre_listeners: Dict[
            SimCallback[Any], Any
        ] = {} if pre_listeners is None else pre_listeners
        self.post_listeners: Dict[
            SimCallback[Any], Any
        ] = {} if post_listeners is None else post_listeners
        self.current_time: datetime = scenario.startDate
        for event in self.event_queue:
            event.validate_ids_exist(sim=self)

    @classmethod
    def _decompose_event(
        cls, event: Event, mission_start_time: datetime
    ) -> List[SimEvent]:
        try:
            primitives = decompose_event(event)
        except OverflowError:
            raise EventDateOverflowError(event)
        result = []
        for primitive in primitives:
            try:
                timestamp = mission_start_time + primitive.mission_time
            except OverflowError:
                raise EventDateOverflowError(event)  # TODO: format this better
            priority = primitive.priority
            if type(primitive) == PropulsiveBurn:
                result.append(
                    BurnEvent(
                        timestamp=timestamp,
                        priority=priority,
                        event=primitive.burn,
                        elements=primitive.elements,
                    )
                )
            else:
                ty = EVENT_TO_SIM_EVENT[type(primitive)]
                result.append(
                    ty(event=primitive, timestamp=timestamp, priority=priority)
                )
        return result

    def _add_event(self, event: SimEvent) -> None:
        self.event_queue.push(event)

    def _pop_next_event(self) -> Optional[SimEvent]:
        return self.event_queue.pop()

    def _process_event(self, event: SimEvent) -> None:
        event.process_with_ctx(sim=self)

    def _run_listeners(self, listeners: Dict[SimCallback[Any], Any]) -> None:
        for listener, arg in listeners.items():
            listeners[listener] = listener(self, arg)

    def _add_error(self, error: SimError) -> None:
        self.errors.append(error)

    def _add_errors(self, errors: Iterable[SimError]) -> None:
        self.errors.extend(errors)

    def _id_exists(self, id_: UUID) -> bool:
        """
        :return: true if id_ exists in this simulation, else false
        """
        return id_ in self.namespace

    def _id_is_of_container(self, id_: UUID) -> bool:
        """
        Check if the provided ID is of a container in this simulation.

        :param id_: id to check; must exist according to _id_exists
        :return: true if id_ corresponds to a container in this simulation, else false
        """
        assert self._id_exists(id_)
        return isinstance(self.namespace[id_], (SimNode, SimEdge)) or isinstance(
            self.namespace[id_].inner, (ElementCarrier, PropulsiveVehicle)
        )

    def _id_is_of_element(self, id_: UUID) -> bool:
        """
        Check if the provided ID is of an element in this simulation.

        :param id_: id to check; must exist according to _id_exists
        :return: true if id_ corresponds to an element in this simulation, else false
        """
        assert self._id_exists(id_)
        return isinstance(self.namespace[id_], SimElement)

    def _id_is_at_location(self, id_: UUID, location: UUID) -> bool:
        """
        Check if the provided ID is an element that exists at ``location``.

        :param id_: id to check; must be an element which exists in this simulation
        :param location: ID of location to check; must be a container and exist in simulation
        :return: true if id is an element that exists at location, else false
        """
        assert self._id_exists(id_)
        assert self._id_exists(location)
        assert self._id_is_of_element(id_)
        assert self._id_is_of_container(location)
        return self.namespace[id_] in self.namespace[location].contents

    def run(self, until: datetime = datetime.max) -> None:
        """
        Run the simulation, consuming the simulation object and returning the resulting errors.

        :return: all errors which resulted from running the simulation
        """
        if not self.event_queue:
            self._run_listeners(self.pre_listeners)
            assert (
                not self.event_queue
            ), "listeners should not modify simulator state, only read it"
        while self.event_queue:
            self._run_listeners(self.pre_listeners)
            next_event = self._pop_next_event()
            assert next_event is not None
            if next_event.timestamp > until:
                break
            self._process_event(next_event)
            self.current_time = next_event.timestamp
            self._run_listeners(self.post_listeners)

    def result(self) -> SimResult:
        return SimResult(
            nodes=list(self.network.keys()),
            edges=[e for adj in self.network.values() for e in adj],
            end_time=self.current_time,
            namespace=self.namespace
        )


def _all_ids_are_elements(
    ids: List[UUID], timestamp: datetime, sim: Simulation
) -> List[SimError]:
    ret = []
    for id_ in ids:
        if not sim._id_exists(id_):
            ret.append(SimError.does_not_exist(timestamp, id_))
            continue
        if not sim._id_is_of_element(id_):
            ret.append(SimError.not_an_element(timestamp, id_))
    return ret


def _all_ids_are_elements_at_location(
    ids: List[UUID], location: UUID, timestamp: datetime, sim: Simulation
) -> List[SimError]:
    ret = []
    for id_ in ids:
        if not sim._id_exists(id_):
            ret.append(SimError.does_not_exist(timestamp, id_))
            continue
        if not sim._id_is_of_element(id_):
            ret.append(SimError.not_an_element(timestamp, id_))
            continue
        if not sim._id_is_at_location(id_, location):
            ret.append(SimError.not_at_location(timestamp, id_, location))
    return ret


def _id_exists_and_is_container(
    id_: UUID, timestamp: datetime, sim: Simulation
) -> List[SimError]:
    ret = []
    if not sim._id_exists(id_):
        ret.append(SimError.does_not_exist(timestamp, id_))
        return ret
    if not sim._id_is_of_container(id_):
        ret.append(SimError.not_a_container(timestamp, id_))
    return ret
