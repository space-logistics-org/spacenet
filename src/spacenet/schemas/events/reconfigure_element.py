"""
Defines object schemas for events that act upon elements.
"""
from uuid import UUID

from pydantic import Field
from typing_extensions import Literal

from .event import Event, EventType


class ReconfigureElement(Event):
    """
    Event that changes the operational state of one instantiated element.

    :param UUID element: unique identifier of the instantiated element to be reconfigured
    :param SafeInt state_index: index of the new operational state
    """

    type: Literal[EventType.RECONFIGURE_ELEMENT] = Field(
        EventType.RECONFIGURE_ELEMENT,
        title="Type",
        description="Event type",
    )
    element: UUID = Field(
        ...,
        description="Unique identifier of the instantiated element to be reconfigured",
    )
    state_index: int = Field(
        ...,
        title="State Index",
        description="Index of the new operational state",
        ge=-1,
    )
