"""
This module defines schemas for specifying events that create, move, update, or delete
elements.
"""
from typing import Dict, List, Union
from typing_extensions import Literal
from uuid import UUID

from pydantic import Field

from .bases import Event, PrimitiveEvent, EventType

from .inst_element import InstElementUUID
from .node import NodeUUID
from .edge import EdgeUUID
from .types import SafeInt

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
    type: Literal[EventType.CreateElements] = Field(
        EventType.CreateElements, title="Type", description="Type of event",
    )
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
    type: Literal[EventType.MoveElements] = Field(
        EventType.MoveElements, title="Type", description="Type of event",
    )
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
    type: Literal[EventType.RemoveElements] = Field(
        EventType.RemoveElements, title="Type", description="Type of event",
    )
    elements: List[InstElementUUID] = Field(
        ..., description="the list of IDs of instantiated elements to remove"
    )


class ReconfigureElements(Event):
    """
    An event which changes the operational state for elements
    at a specific time and location (node or edge).

    :param Dict[InstElementUUID, SafeInt] element_states: a mapping from the IDs of instantiated elements to the index of their desired new state
    """
    type: Literal[EventType.ReconfigureElements] = Field(
        EventType.ReconfigureElements, title="Type", description="Type of event",
    )
    element_states: Dict[InstElementUUID, SafeInt] = Field(
        ...,
        description="a mapping from the IDs of instantiated elements to the index of their desired new state",
    )
