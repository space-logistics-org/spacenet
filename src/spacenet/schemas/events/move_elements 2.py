"""
Defines object schemas for events that act upon elements.
"""
from typing import List
from uuid import UUID

from pydantic import Field
from typing_extensions import Literal

from .event import Event, EventType


class MoveElements(Event):
    """
    Event that moves instantiated elements to a new node, edge, or instantiated
    carrier.

    :param [UUID] elements: list of instantiated elements (by unique identifier) to be moved
    :param UUID container: unique identifier of the node, edge, or instantiated carrier where the elements are to be moved

    """

    type: Literal[EventType.MOVE_ELEMENTS] = Field(
        EventType.MOVE_ELEMENTS,
        title="Type",
        description="Event type",
    )
    elements: List[UUID] = Field(
        ...,
        description="List of instantiated elements (by unique identifier) to be moved",
    )
    container: UUID = Field(
        ...,
        description="Unique identifier of the node, edge, or instantiated carrier where the elements are to be moved",
    )
