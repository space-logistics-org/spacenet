from typing import Callable, Dict, List, Optional, Type, TypeVar, Union

from spacenet.schemas.events import *

PrimitiveEvent = Union[MoveElements, MakeElements, RemoveElements, PropulsiveBurn]

E = TypeVar("E", bound=Event)
P = TypeVar("P", bound=PrimitiveEvent)

DecomposeFn = Callable[[E], List[PrimitiveEvent]]

__all__ = [
    "add_to_decompose_registry",
    "decompose_event"
]


def decompose_move(event: MoveElements) -> List[MoveElements]:
    return [event]


def decompose_make(event: MakeElements) -> List[MakeElements]:
    return [event]


def decompose_remove(event: RemoveElements) -> List[RemoveElements]:
    return [event]


def decompose_propulsive_burn(event: PropulsiveBurn) -> List[PropulsiveBurn]:
    return [event]


def decompose_flight_transport(event: FlightTransport) -> List[PrimitiveEvent]:
    return decompose_move(
        MoveElements(
            priority=event.priority,
            to_move=event.elements_id_list,
            origin_id=event.origin_node_id,
            destination_id=event.destination_node_id,
            mission_time=event.mission_time
        )
    )


def decompose_surface_transport(event: SurfaceTransport) -> List[PrimitiveEvent]:
    return decompose_move(
        MoveElements(
            priority=event.priority,
            to_move=event.elements_id_list,
            origin_id=event.origin_node_id,
            destination_id=event.edge_id,
            mission_time=event.mission_time,
        )
    ) + decompose_move(
        MoveElements(
            priority=event.priority,
            to_move=event.elements_id_list,
            origin_id=event.edge_id,
            destination_id=event.destination_node_id,
            mission_time=event.mission_time
        )
    )


def decompose_space_transport(event: SpaceTransport) -> List[PrimitiveEvent]:
    raise NotImplementedError  # TODO


DECOMPOSE_REGISTRY: Dict[Type[E], DecomposeFn[E]] = {
    MoveElements: decompose_move,
    MakeElements: decompose_make,
    RemoveElements: decompose_remove,
    PropulsiveBurn: decompose_propulsive_burn,
    FlightTransport: decompose_flight_transport,
    SpaceTransport: decompose_space_transport,
    SurfaceTransport: decompose_surface_transport,
}


def add_to_decompose_registry(ty: Type[E], fn: DecomposeFn[E]) -> None:
    DECOMPOSE_REGISTRY[ty] = fn


def decompose_event(event: Event) -> List[PrimitiveEvent]:
    return DECOMPOSE_REGISTRY[type(event)](event)
