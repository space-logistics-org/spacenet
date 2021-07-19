# Simulators have networks and event queues, they take from the event queue, which is sorted
# by time, and re-populate the event queue with new generated events.

# You can model a time-expanded graph in a memory-efficient way by having the contents be the
# time-expanded part.
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set, TypeVar

from pydantic import BaseModel, Field

from spacenet.analysis.min_heap import MinHeap
from spacenet.schemas.element import Element
from spacenet.schemas.edge import Edge
from spacenet.schemas.node import Node
from spacenet.schemas.element_events import (
    MoveElementsEvent,
    MakeElementsEvent,
    RemoveElementsEvent,
)
from spacenet.schemas.burn import Burn


class ContainsElements(BaseModel):
    contains: List["SimElement"] = Field(default_factory=list)


class SimNode(ContainsElements):
    inner: Node


class SimEdge(ContainsElements):
    inner: Edge


class SimElement(ContainsElements):
    inner: Element


class SimEvent(BaseModel, ABC):
    timestamp: datetime
    priority: int

    def __lt__(self, other: "SimEvent") -> bool:
        return (self.timestamp, self.priority) < (other.timestamp, other.priority)

    @abstractmethod
    def process_with_ctx(self, sim: "Simulation"):
        pass


class Move(SimEvent):
    event: MoveElementsEvent

    def process_with_ctx(self, sim: "Simulation"):
        # TODO
        raise NotImplementedError


class Create(SimEvent):
    event: MakeElementsEvent

    def process_with_ctx(self, sim: "Simulation"):
        # TODO
        raise NotImplementedError


class Remove(SimEvent):
    event: RemoveElementsEvent

    def process_with_ctx(self, sim: "Simulation"):
        # TODO
        raise NotImplementedError


class BurnEvent(SimEvent):
    event: Burn

    def process_with_ctx(self, sim: "Simulation"):
        # TODO
        raise NotImplementedError


class SimError(BaseModel):
    timestamp: datetime
    description: str


T = TypeVar("T")
SimCallback = Callable[["Simulation", Optional[T]], T]


class Simulation:
    __slots__ = ("network", "event_queue", "errors", "pre_listeners", "post_listeners")

    # Simulations also need to map ids to entities being simulated

    def __init__(self) -> None:
        # TODO: this should take a campaign mission and build it, or maybe
        #  expose a static method for that
        self.network: Dict[
            SimNode, Set[SimEdge]
        ] = {}  # adjacency list graph representation
        self.event_queue: MinHeap[SimEvent] = MinHeap()
        self.errors: List[SimError] = []
        # Type annotations below aren't tight: Dict is a mapping of SimCallback[T] to T, but
        # different T can be contained in the same dict
        self.pre_listeners: Dict[SimCallback[Any], Any] = {}
        self.post_listeners: Dict[SimCallback[Any], Any] = {}

    def _add_event(self, event: SimEvent) -> None:
        self.event_queue.push(event)

    def _pop_next_event(self) -> Optional[SimEvent]:
        return self.event_queue.pop()

    def _process_event(self, event: SimEvent) -> None:
        event.process_with_ctx(sim=self)

    def _run_listeners(self, listeners: Dict[SimCallback[Any], Any]) -> None:
        for listener, arg in listeners.items():
            listeners[listener] = listener(self, arg)

    def run(self) -> List[SimError]:
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
            self._run_listeners(self.post_listeners)
        return self.errors
