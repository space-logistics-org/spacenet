from typing import Dict, List
from uuid import UUID

from pydantic import Field

from .bases import Event

__all__ = [
    "MakeElements",
    "MoveElements",
    "ReconfigureElements",
    "RemoveElements",
]


class MakeElements(Event):
    """
    An event which brings elements "into" a simulation
    at a specific time and location (node, edge, or inside an element carrier).
    """

    elements: List[UUID] = Field(
        ..., description="the IDs of the elements being added to simulation"
    )
    entry_point_id: UUID = Field(
        ..., description="the ID of the entry point the element is being added at"
    )


class MoveElements(Event):
    """
    An event which moves elements at a specific time and location (node or edge)
    to a new location (node, edge, or element carrier).
    """

    to_move: List[UUID] = Field(
        ..., description="the list of IDs of elements to move"
    )
    origin_id: UUID = Field(
        ...,
        description="the ID of the original time and location "
        "which the elements are being moved from",
    )
    destination_id: UUID = Field(
        ...,
        description="the ID of the new location which the elements are being moved to",
    )


class RemoveElements(Event):
    """
    An event which deletes elements from the simulation
    at a specific time and location (node or edge).
    """

    elements: List[UUID] = Field(
        ..., description="the list of IDs of elements to remove"
    )
    removal_point_id: UUID = Field(
        ..., description="the ID of the node or edge to remove elements from"
    )


class ReconfigureElements(Event):
    """
    An event which changes the operational state for elements
    at a specific time and location (node or edge).
    """

    to_reconfigure: Dict[UUID, UUID] = Field(
        ...,
        description="a mapping from the IDs of elements to the IDs of their desired "
        "new state",
    )
    reconfigure_point_id: UUID = Field(
        ..., description="the ID of the node or edge to reconfigure elements at",
    )
