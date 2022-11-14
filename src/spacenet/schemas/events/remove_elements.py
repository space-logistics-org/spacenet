"""
Defines object schemas for events that act upon elements.
"""
from typing import List
from uuid import UUID

from pydantic import Field
from typing_extensions import Literal

from .event import Event, EventType


class RemoveElements(Event):
    """
    Event that removes instantiated elements.

    :param [UUID] elements: list of instantiated elements (by unique identifier) to be removed
    """

    type: Literal[EventType.REMOVE_ELEMENTS] = Field(
        EventType.REMOVE_ELEMENTS,
        title="Type",
        description="Event type",
    )
    elements: List[UUID] = Field(
        ...,
        description="List of instantiated elements (by unique identifier) to be removed",
    )
