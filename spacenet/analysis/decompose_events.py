from typing import Callable, Dict, List, Type, TypeVar, Union

from spacenet.schemas.events import *

PrimitiveEvent = Union[MoveElements, MakeElements, RemoveElements, PropulsiveBurn]

E = TypeVar("E", bound=Event)
P = TypeVar("P", bound=PrimitiveEvent)

DecomposeFn = Callable[[E], List[PrimitiveEvent]]

__all__ = ["add_to_decompose_registry", "decompose_event"]


def decompose_move(event: MoveElements) -> List[MoveElements]:
    return [event]


def decompose_make(event: MakeElements) -> List[MakeElements]:
    return [event]


def decompose_remove(event: RemoveElements) -> List[RemoveElements]:
    return [event]


def decompose_propulsive_burn(event: PropulsiveBurn) -> List[PropulsiveBurn]:
    return [event]


def move_from_transport(
    transport_event: Union[FlightTransport, SurfaceTransport, SpaceTransport]
) -> List[MoveElements]:
    """
    Construct a sequence of move events from an event which constitutes transporting elements
    from one location to another.

    :param transport_event: event transporting elements
    :return: said event decomposed into multiple simpler move events
    """
    move_to_edge = MoveElements(
            priority=transport_event.priority,
            to_move=transport_event.elements_id_list,
            origin_id=transport_event.origin_node_id,
            destination_id=transport_event.edge_id,
            mission_time=transport_event.mission_time,
            type="MoveElements",
        )
    try:
        move_from_edge = MoveElements(
            priority=transport_event.priority,
            to_move=transport_event.elements_id_list,
            origin_id=transport_event.edge_id,
            destination_id=transport_event.destination_node_id,
            mission_time=transport_event.mission_time + transport_event.exec_time,
            type="MoveElements",
        )
    except OverflowError as oe:
        raise ValueError(oe)
    return [move_to_edge, move_from_edge]


def decompose_flight_transport(event: FlightTransport) -> List[PrimitiveEvent]:
    return [e for move in move_from_transport(event) for e in decompose_move(move)]


def decompose_surface_transport(event: SurfaceTransport) -> List[PrimitiveEvent]:
    return [e for move in move_from_transport(event) for e in decompose_move(move)]


def decompose_space_transport(event: SpaceTransport) -> List[PrimitiveEvent]:
    # TODO: splice in burn into middle later
    return [e for move in move_from_transport(event) for e in decompose_move(move)]


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
    if type(event) not in DECOMPOSE_REGISTRY:
        # fixme
        return []
    return DECOMPOSE_REGISTRY[type(event)](event)
