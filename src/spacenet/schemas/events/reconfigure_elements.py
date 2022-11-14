"""
Defines object schemas for events that act upon elements.
"""
from typing import List
from uuid import UUID

from pydantic import Field
from typing_extensions import Literal

from .event import Event, EventType

from ..elements import StateType


class ReconfigureElements(Event):
    """
    Event that changes the operational state of multiple instantiated elements.

    :param [UUID] elements: list of instantiated elements (by unique identifier) to be reconfigured
    :param StateType state_type: state type to which to be reconfigured
    """

    type: Literal[EventType.RECONFIGURE_ELEMENTS] = Field(
        EventType.RECONFIGURE_ELEMENTS,
        title="Type",
        description="Event type",
    )
    elements: List[UUID] = Field(
        ...,
        description="List of instantiated elements (by unique identifier) to be reconfigured",
    )
    state_type: StateType = Field(
        ...,
        description="State type to which to be reconfigured",
    )
