"""
This module defines a function for turning events into multiple "simpler" events,
and a mechanism for registering types of events with a function to do so.
"""
from typing import Callable, Dict, List, Type, TypeVar, Union

from spacenet.schemas import Burn
from spacenet.schemas.events import *

PrimitiveEvents = Union[MoveElements, CreateElements, RemoveElements, PropulsiveBurn]

E = TypeVar("E", bound=Event)
P = TypeVar("P", bound=PrimitiveEvents)

DecomposeFn = Callable[[E], List[PrimitiveEvents]]

__all__ = ["add_to_decompose_registry", "decompose_event"]


def _decompose_move(event: MoveElements) -> List[MoveElements]:
    """
    Decompose an event moving elements into a list of MoveElements events representing the
    same action.

    :param event: event to decompose
    :return: list of events representing the same action
    """
    return [event]


def _decompose_make(event: CreateElements) -> List[CreateElements]:
    """
    Decompose an event creating elements into a list of CreateElements events representing the
    same action.

    :param event: event to decompose
    :return: list of events representing the same action
    """
    return [event]


def _decompose_remove(event: RemoveElements) -> List[RemoveElements]:
    """
    Decompose an event removing elements into a list of RemoveElements events representing the
    same action.

    :param event: event to decompose
    :return: list of events representing the same action
    """
    return [event]


def _decompose_propulsive_burn(event: PropulsiveBurn) -> List[PropulsiveBurn]:
    """
    Decompose an event burning and staging elements into a list of PropulsiveBurn events
    representing the same action.

    :param event: event to decompose
    :return: list of events representing the same action
    """
    return [event]


def move_from_transport(
    transport_event: Union[FlightTransport, SurfaceTransport, SpaceTransport]
) -> List[MoveElements]:
    """
    Construct a sequence of MoveElements events from an event which constitutes transporting
    elements from one node to another.

    :param transport_event: event transporting elements
    :return: said event decomposed into multiple simpler move events
    :raises OverflowError: if mission_time + exec_time > maximum timedelta
    """
    move_to_edge = MoveElements(
        name=f"Move from {transport_event.origin_node_id} to {transport_event.edge_id}",
        priority=transport_event.priority,
        to_move=transport_event.elements_id_list,
        origin_id=transport_event.origin_node_id,
        destination_id=transport_event.edge_id,
        mission_time=transport_event.mission_time,
        type="MoveElements",
    )
    move_from_edge = MoveElements(
        name=f"Move from {transport_event.edge_id} to {transport_event.destination_node_id}",
        priority=transport_event.priority,
        to_move=transport_event.elements_id_list,
        origin_id=transport_event.edge_id,
        destination_id=transport_event.destination_node_id,
        mission_time=transport_event.mission_time + transport_event.exec_time,
        queued_at=transport_event.mission_time,
        type="MoveElements",
    )
    return [move_to_edge, move_from_edge]


def _decompose_flight_transport(event: FlightTransport) -> List[PrimitiveEvents]:
    """
    Decompose an event transporting elements from one node to another via flight into a list
    of primitive events representing the same action.

    :param event: event to decompose
    :return: list of primitive events representing the same action
    """
    return [e for move in move_from_transport(event) for e in _decompose_move(move)]


def _decompose_surface_transport(event: SurfaceTransport) -> List[PrimitiveEvents]:
    """
    Decompose an event transporting elements from one node to another via surface transit
    into a list of primitive events representing the same action.

    :param event: event to decompose
    :return: list of primitive events representing the same action
    """
    return [e for move in move_from_transport(event) for e in _decompose_move(move)]


def _decompose_space_transport(event: SpaceTransport) -> List[PrimitiveEvents]:
    """
    Decompose an event transporting elements from one node to another via space transit
    into a list of primitive events representing the same action.

    :param event: event to decompose
    :return: list of primitive events representing the same action
    """
    assert (
        event.delta_v is not None
    ), f"Expected event {event.name} to have a defined delta-v"
    burn = Burn(edge_id=event.edge_id, time=event.mission_time, delta_v=event.delta_v)
    burn_stage_sequence = [
        burn_or_stage
        for sequence in event.burnStageProfile
        for burn_or_stage in sequence.burn_stage_sequence
    ]
    involved_elements = list(
        set(
            event.elements_id_list
            + [burn_or_stage.element_id for burn_or_stage in burn_stage_sequence]
        )
    )
    burn_event = PropulsiveBurn(
        name=f"Burn @ {event.edge_id}",
        type="PropulsiveBurn",
        priority=event.priority,
        mission_time=event.mission_time,
        elements=involved_elements,
        burn=burn,
        burn_stage_sequence=burn_stage_sequence,
    )
    moves: List[PrimitiveEvents] = [
        e for move in move_from_transport(event) for e in _decompose_move(move)
    ]
    moves.insert(1, burn_event)
    return moves


DECOMPOSE_REGISTRY: Dict[Type[E], DecomposeFn[E]] = {
    MoveElements: _decompose_move,
    CreateElements: _decompose_make,
    RemoveElements: _decompose_remove,
    PropulsiveBurn: _decompose_propulsive_burn,
    FlightTransport: _decompose_flight_transport,
    SpaceTransport: _decompose_space_transport,
    SurfaceTransport: _decompose_surface_transport,
}


def add_to_decompose_registry(ty: Type[E], fn: DecomposeFn[E]) -> None:
    """
    Register a function ``fn`` for decomposing events of type ``ty`` into primitive events.

    :param ty: event type to associate function with
    :param fn: function which decomposes ty
    """
    DECOMPOSE_REGISTRY[ty] = fn


def decompose_event(event: Event) -> List[PrimitiveEvents]:
    """
    Decompose an event into a list of primitives which represent the same action.

    :param event: event to decompose
    :return: list of events representing the same action
    """
    if type(event) not in DECOMPOSE_REGISTRY:
        return []
    return DECOMPOSE_REGISTRY[type(event)](event)
