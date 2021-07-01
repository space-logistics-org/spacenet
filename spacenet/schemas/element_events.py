from typing import Dict, List

from pydantic import BaseModel, Field

from .types import SafeInt

__all__ = [
    "MakeElementsEvent",
    "MoveElementsEvent",
    "ReconfigureElementsEvent",
    "RemoveElementsEvent",
]


class MakeElementsEvent(BaseModel):
    """
    An event which brings elements "into" a simulation
    at a specific time and location (node, edge, or inside an element carrier).
    """

    element_id: List[SafeInt] = Field(
        ..., description="the IDs of the elements being added to simulation"
    )
    entry_point_id: SafeInt = Field(
        ..., description="the ID of the entry point the element is being added at"
    )


class MoveElementsEvent(BaseModel):
    """
    An event which moves elements at a specific time and location (node or edge)
    to a new location (node, edge, or element carrier).
    """

    to_move: List[SafeInt] = Field(
        ..., description="the list of IDs of elements to move"
    )
    origin_id: SafeInt = Field(
        ...,
        description="the ID of the original time and location "
        "which the elements are being moved from",
    )
    destination_id: SafeInt = Field(
        ...,
        description="the ID of the new location which the elements are being moved to",
    )


class RemoveElementsEvent(BaseModel):
    """
    An event which deletes elements from the simulation
    at a specific time and location (node or edge).
    """

    to_remove: List[SafeInt] = Field(
        ..., description="the list of IDs of elements to remove"
    )
    removal_point_id: SafeInt = Field(
        ..., description="the ID of the node or edge to remove elements from"
    )


class ReconfigureElementsEvent(BaseModel):
    """
    An event which changes the operational state for elements
    at a specific time and location (node or edge).
    """

    to_reconfigure: Dict[SafeInt, SafeInt] = Field(
        ...,
        description="a mapping from the IDs of elements to the IDs of their desired "
        "new state",
    )
    reconfigure_point_id: SafeInt = Field(
        ..., description="the ID of the node or edge to reconfigure elements at",
    )
