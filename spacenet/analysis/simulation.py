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
    Scenario,
    Element,
    Edge,
    MoveElements,
    MakeElements,
    RemoveElements,
)
from spacenet.schemas.node import Node

__all__ = ["Simulation"]


class ContainsElements(BaseModel):
    contents: List["SimElement"] = Field(default_factory=list)


class SimNode(ContainsElements):
    """
    A node under simulation; wraps Node schema.
    """

    inner: Node  # TODO: this should be some type that has UUID IDs, not int IDs


class SimEdge(ContainsElements):
    """
    An edge under simulation; wraps Edge schema.
    """

    inner: Edge  # TODO: this should be some type that has UUID IDs, not int IDs


class SimElement(ContainsElements):
    """
    An element under simulation; wraps Element schema.
    """

    inner: Element  # TODO: this should be some type that has UUID IDs, not int IDs


class SimEvent(BaseModel, ABC):
    """
    An event in simulation.
    """

    timestamp: datetime
    priority: int

    def __lt__(self, other: "SimEvent") -> bool:
        return (self.timestamp, self.priority) < (other.timestamp, other.priority)

    @abstractmethod
    def process_with_ctx(self, sim: "Simulation") -> None:
        pass


class Move(SimEvent):
    """
    Represents an event moving elements, one of the four primitive SimEvents.
    """

    event: MoveElements

    def process_with_ctx(self, sim: "Simulation") -> None:
        # Move all elements in the list to the new destination
        # Possible errors:
        #   source is not a container -> error for each moved element
        #   destination is not a container -> error for each moved element
        #   some element in the list is not actually an element
        # TODO: can decompose a move into a remove and a create
        prev_error_count = len(sim.errors)
        source = self.event.origin_id
        if not sim.id_exists(source):
            sim.add_error(SimError.does_not_exist(self.timestamp, source))
        else:
            if not sim.id_is_of_container(source):
                sim.add_error(SimError.not_a_container(self.timestamp, source))
        dest = self.event.destination_id
        # TODO: refactor: code duplication
        if not sim.id_exists(dest):
            sim.add_error(SimError.does_not_exist(self.timestamp, dest))
        else:
            if not sim.id_is_of_container(dest):
                sim.add_error(SimError.not_a_container(self.timestamp, dest))
        for id_ in self.event.to_move:
            if not sim.id_exists(id_):
                sim.add_error(SimError.does_not_exist(self.timestamp, id_))
            else:
                if not sim.id_is_of_element(id_):
                    sim.add_error(SimError.not_an_element(self.timestamp, id_))
        if len(sim.errors) == prev_error_count:
            # Filter source contents and move them over
            prev_contents = sim.namespace[source].contents
            # fixme Low-hanging fruit for optimization:
            #  store UUIDs in elements and check those instead? Performance
            new_contents = [
                element
                for element in prev_contents
                if element not in self.event.to_move
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

    def process_with_ctx(self, sim: "Simulation") -> None:
        # Create all elements in the list at the specified location
        # Possible errors:
        #   location is not a container -> error for each created element
        #   values in the list don't correspond to actual elements
        prev_error_count = len(sim.errors)
        entry_point = self.event.entry_point_id
        if not sim.id_exists(entry_point):
            sim.add_error(SimError.does_not_exist(self.timestamp, entry_point))
        else:
            if not sim.id_is_of_container(entry_point):
                sim.add_error(SimError.not_a_container(self.timestamp, entry_point))
        for id_ in self.event.elements:
            if not sim.id_exists(id_):
                sim.add_error(SimError.does_not_exist(self.timestamp, id_))
            else:
                if not sim.id_is_of_element(id_):
                    sim.add_error(SimError.not_an_element(self.timestamp, id_))
        if len(sim.errors) == prev_error_count:
            sim.namespace[entry_point].contents.extend(
                sim.namespace[id_] for id_ in self.event.elements
            )


class Remove(SimEvent):
    """
    Represents an event removing elements, one of the four primitive SimEvents.
    """

    event: RemoveElements

    def process_with_ctx(self, sim: "Simulation") -> None:
        # Remove all elements in the list at the specified location
        # Possible errors:
        #   location is not a container -> error for each created element
        #   values in the list don't correspond to actual elements
        #   elements provided aren't actually at the specified location
        prev_error_count = len(sim.errors)
        removal_point_id = self.event.removal_point_id
        if not sim.id_exists(removal_point_id):
            sim.add_error(SimError.does_not_exist(self.timestamp, removal_point_id))
        else:
            if not sim.id_is_of_container(self.event.removal_point_id):
                sim.add_error(
                    SimError.not_a_container(
                        self.timestamp, self.event.removal_point_id
                    )
                )
        for id_ in self.event.elements:
            if not sim.id_exists(id_):
                sim.add_error(SimError.does_not_exist(self.timestamp, id_))
            else:
                if not sim.id_is_of_element(id_):
                    sim.add_error(SimError.not_an_element(self.timestamp, id_))
                else:
                    if not sim.id_is_at_location(id_, removal_point_id):
                        sim.add_error(
                            SimError.not_at_location(
                                self.timestamp, id_, removal_point_id
                            )
                        )
        if len(sim.errors) == prev_error_count:  # no errors
            prev_contents = sim.namespace[removal_point_id].contents
            # fixme Low-hanging fruit for optimization:
            #  store UUIDs in elements and check those instead? Performance
            new_contents = [
                element
                for element in prev_contents
                if element not in self.event.elements
            ]
            sim.namespace[removal_point_id].contents = new_contents


class BurnEvent(SimEvent):
    """
    Represents a burn, one of the four primitive SimEvents.
    """

    event: Burn
    elements: List[UUID]  # ordered: last element is first to have delta-v consumed

    def process_with_ctx(self, sim: "Simulation") -> None:
        # TODO
        # Consume the fuel at the given elements until enough fuel has been consumed
        # to satisfy delta-v requirement
        # Possible errors:
        #   values in the list don't correspond to actual elements
        #   not enough fuel (if this is a problem depends, but it's probably more efficient to
        #    just not add burn events if there's no fuel constraint and just stage)
        raise NotImplementedError


class SimError(BaseModel):
    timestamp: datetime
    description: str

    @staticmethod
    def does_not_exist(timestamp: datetime, id_: UUID) -> "SimError":
        return SimError(
            timestamp=timestamp, description=f"No entity with id {id_} in namespace"
        )

    @staticmethod
    def not_an_element(timestamp: datetime, id_: UUID) -> "SimError":
        return SimError(timestamp=timestamp, description=f"ID {id_} is not an element")

    @staticmethod
    def not_a_container(timestamp: datetime, id_: UUID) -> "SimError":
        return SimError(timestamp=timestamp, description=f"ID {id_} is not a container")

    @staticmethod
    def not_at_location(timestamp: datetime, id_: UUID, location: UUID) -> "SimError":
        return SimError(
            timestamp=timestamp, description=f"ID {id_} is not at location {location}"
        )


T = TypeVar("T")
SimCallback = Callable[["Simulation", Optional[T]], T]


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
        pre_listeners: Optional[Dict[SimCallback[Any], Any]],
        post_listeners: Optional[Dict[SimCallback[Any], Any]],
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
            for atomic_event in Simulation._decompose_event(event)
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

    @classmethod
    def _decompose_event(cls, event) -> List[SimEvent]:
        # TODO
        # Honestly events should implement this but that might cause circular import problems
        pass

    def _add_event(self, event: SimEvent) -> None:
        self.event_queue.push(event)

    def _pop_next_event(self) -> Optional[SimEvent]:
        return self.event_queue.pop()

    def _process_event(self, event: SimEvent) -> None:
        event.process_with_ctx(sim=self)

    def _run_listeners(self, listeners: Dict[SimCallback[Any], Any]) -> None:
        for listener, arg in listeners.items():
            listeners[listener] = listener(self, arg)

    def add_error(self, error: SimError) -> None:
        self.errors.append(error)

    def add_errors(self, errors: Iterable[SimError]) -> None:
        self.errors.extend(errors)

    def id_exists(self, id_: UUID) -> bool:
        return id_ in self.namespace

    def id_is_of_container(self, id_: UUID) -> bool:
        assert self.id_exists(id_)
        return isinstance(self.namespace[id_], (SimNode, SimEdge)) or isinstance(
            self.namespace[id_].inner, ElementCarrier
        )

    def id_is_of_element(self, id_: UUID) -> bool:
        assert self.id_exists(id_)
        return isinstance(self.namespace[id_], SimElement)

    def id_is_at_location(self, id_: UUID, location: UUID) -> bool:
        assert self.id_exists(id_)
        assert self.id_exists(location)
        assert self.id_is_of_element(id_)
        assert self.id_is_of_container(location)
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
