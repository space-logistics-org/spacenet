"""
This module defines schemas for specifying events that create, move, update, or delete
elements.
"""
from typing import Dict, List, Union
from uuid import UUID

from pydantic import Field

from .bases import Event, PrimitiveEvent

from .inst_element import InstElement, InstElementUUID
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
    """
    elements: List[InstElementUUID] = Field(
        ..., description="the IDs of the instantiated elements being added to simulation"
    )
    location: Union[EdgeUUID, InstElementUUID, NodeUUID] = Field(
        ..., description="the ID of the node, edge or instianted element where the element is being created"
    )


class MoveElements(PrimitiveEvent):
    """
    An event which moves elements at a specific time and location (node or edge)
    to a new location (node, edge, or element carrier).
    """

    elements: List[InstElementUUID] = Field(..., description="the list of IDs of instantiated elements to move")
    location: Union[EdgeUUID, NodeUUID] = Field(
        ...,
        description="the ID of the original edge or node "
        "which the elements are being moved from",
    )
    container: Union[EdgeUUID, InstElementUUID, NodeUUID] = Field(
        ...,
        description="the ID of the new location which the elements are being moved to",
    )


class RemoveElements(PrimitiveEvent):
    """
    An event which deletes elements from the simulation
    at a specific time and location (node or edge).
    """

    elements: List[InstElementUUID] = Field(
        ..., description="the list of IDs of instantiated elements to remove"
    )
    location: Union[NodeUUID, EdgeUUID]  = Field(
        ..., description="the ID of the node or edge to remove elements from"
    )


class ReconfigureElements(Event):
    """
    An event which changes the operational state for elements
    at a specific time and location (node or edge).
    """

    element_states: Dict[InstElementUUID, StateUUID] = Field(
        ...,
        description="a mapping from the IDs of instantiated elements to the IDs of their desired "
        "new state",
    )
    location: Union[NodeUUID, EdgeUUID] = Field(
        ..., description="the ID of the node or edge to reconfigure elements at",
    )
