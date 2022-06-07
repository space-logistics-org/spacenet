"""
This module defines schemas for specifying events that create, move, update, or delete
elements.
"""
from typing import Dict, List, Union
from uuid import UUID

from pydantic import Field

from .bases import Event, PrimitiveEvent

from .inst_element import InstElementUUID
from .node import NodeUUID
from .edge import EdgeUUID
from .state import StateUUID

__all__ = [
    "CreateElements",
    "MoveElements",
    "ReconfigureElements",
    "RemoveElements",
]


class CreateElements(PrimitiveEvent):
    """
    An event which brings elements "into" a simulation
    at a specific time and location (node, edge, or inside an element carrier).

    :param [InstElementUUID] elements: list of the UUIDs of the instantiated elements being added to simulation
    :param EdgeUUID | InstElementUUID | NodeUUID container: the UUID of the node, edge or instianted element where the element is being created
    """
    elements: List[InstElementUUID] = Field(
        ..., description="the UUIDs of the instantiated elements being added to simulation"
    )
    container: Union[EdgeUUID, InstElementUUID, NodeUUID] = Field(
        ..., description="the UUID of the node, edge or instianted element where the element is being created"
    )


class MoveElements(PrimitiveEvent):
    """
    An event which moves elements at a specific time and location (node or edge)
    to a new location (node, edge, or element carrier).

    :param [InstElementUUID] elements: list of the UUIDs of the instantiated elements being moved
    :param EdgeUUID | InstElementUUID | NodeUUID container: the UUID of the node, edge or instianted element to which the elements are being moved

    """

    elements: List[InstElementUUID] = Field(..., description="the list of IDs of instantiated elements to move")
    container: Union[EdgeUUID, InstElementUUID, NodeUUID] = Field(
        ...,
        description="the ID of the new location which the elements are being moved to",
    )


class RemoveElements(PrimitiveEvent):
    """
    An event which deletes elements from the simulation
    at a specific time and location (node or edge).

    :param [InstElementUUID] elements: list of the UUIDs of the instantiated elements being removed
    """

    elements: List[InstElementUUID] = Field(
        ..., description="the list of IDs of instantiated elements to remove"
    )


class ReconfigureElements(Event):
    """
    An event which changes the operational state for elements
    at a specific time and location (node or edge).

    :param Dict[InstElementUUID, StateUUID] element_states: a mapping from the IDs of instantiated elements to the IDs of their desired new state
    """
    #TODO: change to SafeInts?
    element_states: Dict[InstElementUUID, StateUUID] = Field(
        ...,
        description="a mapping from the IDs of instantiated elements to the IDs of their desired "
        "new state",
    )
