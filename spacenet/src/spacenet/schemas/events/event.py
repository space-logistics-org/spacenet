"""Defines object schemas for generic events."""

from abc import ABC
from datetime import timedelta
from uuid import UUID
from enum import Enum

from pydantic import Field
from fastapi_camelcase import CamelModel


class EventType(str, Enum):
    """
    Enumeration of event types.
    """

    ADD_RESOURCES = "Add Resources"
    TRANSFER_RESOURCES = "Transfer Resources"
    CONSUME_RESOURCES = "Consume Resources"
    CREATE_ELEMENTS = "Create Elements"
    MOVE_ELEMENTS = "Move Elements"
    REMOVE_ELEMENTS = "Remove Elements"
    RECONFIGURE_ELEMENTS = "Reconfigure Elements"
    RECONFIGURE_ELEMENT = "Reconfigure Element"
    FLIGHT_TRANSPORT = "Flight Transport"
    PROPULSIVE_BURN = "Propulsive Burn"
    SPACE_TRANSPORT = "Space Transport"
    SURFACE_TRANSPORT = "Surface Transport"
    CREWED_EVA = "Crewed EVA"
    CREWED_EXPLORATION = "Crewed Exploration"


class Event(CamelModel, ABC):
    """
    Abstract base for an event.

    :param str name: event name
    :param EventType type: event type
    :param int priority: prioritization for coincident events (ranges between 1 and 5 inclusive)
    :param timedelta mission_time: event time relative to the start of the mission
    :param UUID location: event location unique identifier
    """

    name: str = Field(..., description="Event name")
    type: EventType = Field(..., title="Type", description="Event type")
    priority: int = Field(
        ...,
        title="Priority",
        description="Prioritization for coincident events",
        ge=1,
        le=5,
    )
    mission_time: timedelta = Field(
        ...,
        title="Mission Time",
        description="Event time relative to the start of the mission",
    )
    location: UUID = Field(
        ..., title="Location", description="Event location unique identifier"
    )
