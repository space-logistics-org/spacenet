# Simulators have networks and event queues, they take from the event queue, which is sorted
# by time, and re-populate the event queue with new generated events.

# You can model a time-expanded graph in a memory-efficient way by having the contents be the
# time-expanded part.
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from heapq import heappop, heappush
from typing import Callable, Dict, List, Optional, Set, Tuple

from spacenet.schemas.element import Element
from spacenet.schemas.edge import Edge
from spacenet.schemas.node import Node


class SimEntity(ABC):
    @abstractmethod
    def at(self, timestamp: datetime) -> Tuple["SimElement", ...]:
        pass


@dataclass()
class SimNode:
    inner: Node
    contains: List["SimElement"] = field(default_factory=list)


@dataclass()
class SimEdge:
    inner: Edge
    contains: List["SimElement"] = field(default_factory=list)


@dataclass()
class SimElement:
    inner: Element
    contains: List["SimElement"] = field(default_factory=list)


@dataclass()
class SimEvent:
    timestamp: datetime
    priority: int

    # TODO: other fields, perhaps subclasses?

    def __lt__(self, other: "SimEvent") -> bool:
        return (self.timestamp, self.priority) < (other.timestamp, other.priority)


@dataclass()
class SimError:
    timestamp: datetime

    # tell sim events how they're processed / how they modify a simulation


class Simulation:
    __slots__ = ("network", "event_queue", "errors", "pre_listeners", "post_listeners")
    # Simulations also need to map ids to entities being simulated
    # TODO: make it possible to register functions which perform actions upon changes
    #  (each time an event is processed)

    def __init__(self) -> None:
        # TODO: this should take a campaign mission and build it, or maybe
        #  expose a static method for that
        self.network: Dict[
            SimNode, Set[SimEdge]
        ] = {}  # adjacency list graph representation
        self.event_queue: List[SimEvent] = []  # min-heap of events
        self.errors: List[SimError] = []
        self.pre_listeners: List[Callable[['Simulation'], None]] = []
        self.post_listeners: List[Callable[['Simulation'], None]] = []

    def _add_event(self, event: SimEvent) -> None:
        heappush(self.event_queue, event)

    def _pop_next_event(self) -> Optional[SimEvent]:
        if not self.event_queue:
            return None
        return heappop(self.event_queue)

    def _process_event(self, event: SimEvent) -> None:
        # TODO
        # Apply the effects of the provided event, mutating the current state
        pass

    def run(self) -> List[SimError]:
        # TODO: pre here?
        while self.event_queue:
            for listener in self.pre_listeners:
                listener(self)
            next_event = self._pop_next_event()
            assert next_event is not None
            self._process_event(next_event)
            for listener in self.post_listeners:
                listener(self)
        return self.errors
