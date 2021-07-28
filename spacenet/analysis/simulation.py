# Simulators have networks and event queues, they take from the event queue, which is sorted
# by time, and re-populate the event queue with new generated events.

# You can model a time-expanded graph in a memory-efficient way by having the contents be the
# time-expanded part.
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Callable, Dict, Iterable, List, Optional, Set, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel, Field

from spacenet.analysis.min_heap import MinHeap
from spacenet.schemas import (
    Burn,
    ElementCarrier,
    Event,
    PropulsiveBurn,
    Scenario,
    Element,
    UUIDEdge,
    MoveElements,
    MakeElements,
    RemoveElements,
)
from spacenet.schemas.node import Node
from .decompose_events import decompose_event
from .simulation_errors import SimError

from spacenet.fuel_formulas.functions import *

__all__ = ["Simulation"]


class ContainsElements(BaseModel):
    contents: List["SimElement"] = Field(default_factory=list)


class SimElement(ContainsElements):
    """
    An element under simulation; wraps Element schema.
    """

    inner: Element


ContainsElements.update_forward_refs()


class SimNode(ContainsElements):
    """
    A node under simulation; wraps Node schema.
    """

    inner: Node  # fixme: types: should be union

    def __hash__(self):
        # This is safe because, assuming Node is safe to hash, we don't hash the mutable
        # state in contents
        return hash(self.inner)


class SimEdge(ContainsElements):
    """
    An edge under simulation; wraps Edge schema.
    """

    inner: UUIDEdge  # fixme: types: should be union


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
        :raise ValueError: if this event has referenced values not present
        in the namespace
        """
        pass

    @abstractmethod
    def process_with_ctx(self, sim: "Simulation") -> None:
        pass


class Move(SimEvent):
    """
    Represents an event moving elements, one of the four primitive SimEvents.
    """

    event: MoveElements

    def validate_ids_exist(self, sim: "Simulation") -> None:
        event = self.event
        if not sim._id_exists(event.origin_id):
            raise ValueError(f"Origin id {event.origin_id} does not exist")
        elif not sim._id_exists(event.destination_id):
            raise ValueError(f"Destination id {event.destination_id} does not exist")
        for id_  in event.to_move:
            if not sim._id_exists(id_):
                raise ValueError(f"ID {id_} does not exist")

    def process_with_ctx(self, sim: "Simulation") -> None:
        # Move all elements in the list to the new destination
        # Possible errors:
        #   source is not a container -> error for each moved element
        #   destination is not a container -> error for each moved element
        #   some element in the list is not actually an element
        # TODO: can decompose a move into a remove and a create?
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
        # TODO: if source doesn't exist you sort of can't continue
        # fixme Low-hanging fruit for optimization:
        #  store UUIDs in elements and check those instead? Performance
        new_contents = [
            element for element in prev_contents if element not in self.event.to_move
        ]
        sim.namespace[source].contents = new_contents
        sim.namespace[dest].contents.extend(
            sim.namespace[id_] for id_ in self.event.to_move
        )


class Create(SimEvent):
    """
    Represents an event creating elements, one of the four primitive SimEvents.
    """

    event: MakeElements

    def validate_ids_exist(self, sim: "Simulation") -> None:
        event = self.event
        if not sim._id_exists(event.entry_point_id):
            raise ValueError(f"Entry point {event.entry_point_id} does not exist")
        for id_ in event.elements:
            if not sim._id_exists(id_):
                raise ValueError(f"ID {id_} does not exist")

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
            raise ValueError()
        for id_ in event.elements:
            if not sim._id_exists(id_):
                raise ValueError()

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
        # fixme Low-hanging fruit for optimization:
        #  store UUIDs in elements and check those instead? Performance
        new_contents = [
            element for element in prev_contents if element not in self.event.elements
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
        
        #delta_ve = event.delta_v
        #for element in elements:
            #init_mass = element.mass
            #fin_mass = final_mass_from(delta_v: delta_ve, isp: 0, m_0: init_mass)
            #req_deltav = delts_v_from(isp: 0, m_0: init_mass, m_f: fin_mass)
            #if (req_deltav > delta_ve):
                #subtract mass/fuel
            #else:
                #delta_ve -= req_deltav
                #RemoveElement? stage


T = TypeVar("T")
SimCallback = Callable[["Simulation", Optional[T]], T]


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

    # Simulations also need to map ids to entities being simulated

    def __init__(
        self,
        scenario: Scenario,
        # TODO: write function to test scenario, call it here?
        pre_listeners: Optional[Dict[SimCallback[Any], Any]] = None,
        post_listeners: Optional[Dict[SimCallback[Any], Any]] = None,
    ) -> None:
        self.network: Dict[
            SimNode, Set[SimEdge]
        ] = {}  # adjacency list graph representation
        for id_, edge in scenario.network.edges.items():
            pass
            # add edges to adj-list rep
            # TODO: origin_id refers to DB id but has to correspond to the UUID of the edge
        for id_, node in scenario.network.nodes.items():
            self.network.setdefault(SimNode(inner=node), set())
        events = [
            atomic_event
            for mission in scenario.missionList
            for event in mission.events
            for atomic_event in Simulation._decompose_event(event, mission.start_date)
        ]
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
        self.namespace: Dict[UUID, Union[SimElement, SimNode, SimEdge]] = {}
        for id_, node in scenario.network.nodes.items():
            self.namespace[id_] = SimNode(inner=node)
        for id_, edge in scenario.network.edges.items():
            self.namespace[id_] = SimEdge(inner=edge)
        for id_, element in scenario.elementList.items():
            self.namespace[id_] = SimElement(inner=element)
        assert len(scenario.network.nodes) + len(scenario.network.edges) + len(
            scenario.elementList
        ) == len(self.namespace), "expected no duplicate IDs"
        self.current_time: datetime = scenario.startDate
        for event in self.event_queue:
            event.validate_ids_exist(sim=self)

    @classmethod  # TODO: staticmethod?
    def _decompose_event(
        cls, event: Event, mission_start_time: datetime
    ) -> List[SimEvent]:
        result = []
        for primitive in decompose_event(event):
            timestamp = mission_start_time + primitive.mission_time
            # TODO: this can overflow. That's an invalid event? So should valueerror
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
            self.namespace[id_].inner, ElementCarrier
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

    def run(self) -> List[SimError]:
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
            self._process_event(next_event)
            self.current_time = next_event.timestamp
            self._run_listeners(self.post_listeners)
        return self.errors


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
