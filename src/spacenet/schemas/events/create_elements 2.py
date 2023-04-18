"""
Defines object schemas for events that act upon elements.
"""
from typing import List
from uuid import UUID

from pydantic import Field
from typing_extensions import Literal

from .event import Event, EventType


class CreateElements(Event):
    """
    Event that creates instantiated elements inside a node, edge, or
    instantiated element carrier.
    """

    type: Literal[EventType.CREATE_ELEMENTS] = Field(
        EventType.CREATE_ELEMENTS,
        title="Type",
        description="Event type",
    )
    elements: List[UUID] = Field(
        ...,
        description="List of instantiated elements (by unique identifier) to be created",
    )
    container: UUID = Field(
        ...,
        description="Node, edge, or instantiated carrier where the elements are to be created",
    )
