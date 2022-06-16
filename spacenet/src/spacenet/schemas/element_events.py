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
    "ReconfigureElement",
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
    elements: List[UUID] = Field(
        ..., description="the UUIDs of the instantiated elements being added to simulation"
    )
    container: UUID = Field(
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
    elements: List[UUID] = Field(..., description="the list of IDs of instantiated elements to move")
    container: UUID = Field(
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
    elements: List[UUID] = Field(
        ..., description="the list of IDs of instantiated elements to remove"
    )

class ReconfigureElement(Event):
    """
    An event which changes the operational state for an individual element
    at a specific time and location (node or edge).

    :param UUID element: UUID of the element whose state is to be changed
    :param SafeInt state_index: index of the element's new operational state
    """
    type: Literal[EventType.ReconfigureElement] = Field(
        EventType.ReconfigureElement, title="Type", description="Type of event",
    )
    element: UUID = Field(
        ...,
        description="UUID of the element whose state is to be changed",
    )
    state_index: SafeInt = Field(..., title="State Index", description="index of the element's new operational state")

class ReconfigureElements(Event):
    """
    An event which changes the operational state for elements
    at a specific time and location (node or edge).

    :param Dict[InstElementUUID, SafeInt] element_states: a mapping from the IDs of instantiated elements to the index of their desired new state
    """
    type: Literal[EventType.ReconfigureElements] = Field(
        EventType.ReconfigureElements, title="Type", description="Type of event",
    )
    element_states: Dict[UUID, SafeInt] = Field(
        ...,
        description="a mapping from the IDs of instantiated elements to the index of their desired new state",
    )
