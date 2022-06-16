"""
This module defines base classes for events.
"""
from datetime import timedelta
from uuid import UUID
from typing import Union
from enum import Enum

from pydantic import BaseModel, Field, validator
from fastapi_camelcase import CamelModel

__all__ = ["Event", "EventType", "ElementTransportEvent", "PrimitiveEvent"]

class EventType(str, Enum):
    """
    An enumeration of all the types of events
    """

    ConsumeResources = "Consume Resources"
    TransferResources = "Transfer Resources"
    CreateElements = "Create Elements"
    MoveElements = "Move Elements"
    RemoveElements = "Remove Elements"
    ReconfigureElements = "Reconfigure Elements"
    ReconfigureElement = "Reconfigure Element"
    FlightTransport = "Flight Transport"
    PropulsiveBurn = "Propulsive Burn"
    SpaceTransport = "Space Transport"
    SurfaceTransport = "Surface Transport"
    CrewedEVA = "Crewed EVA"
    CrewedExploration = "Crewed Exploration"



class Event(CamelModel):
    """
    The base event schema.

    :param str name: the name of the event
    :param int priority: the importance of the mission event, represented by an integer between 1 and 5
    :param timedelta mission_time: the time this event starts at, relative to the start of the mission
    :param UUID location: the UUID of the node or edge at which the event begins
    """
    name: str = Field(..., description="The name of the event")
    type: str = Field(..., title="Type", description="The type of event")
    priority: int = Field(
        ...,
        title="Priority",
        description="The importance of the mission event",
        ge=1,
        le=5,
    )
    mission_time: timedelta = Field(
        ...,
        title="Mission Time",
        description="The time this event starts at, relative to the start of the mission",
    ),
    location: UUID = Field(..., title="Location", description="The UUID of the node or edge at which the event begins")


class ElementTransportEvent(Event):
    """
    A schema representing a basic event transporting elements from one node to another.

    :param UUID edge: the UUID of the edge along which this transport event traverses
    """

    edge: UUID = Field(
        ..., description="The UUID of the edge along which this transport event traverses"
    )



class PrimitiveEvent(Event):
    """
    A schema representing events which other events are decomposed into.
    """

    queued_at: timedelta = None

    @validator("queued_at", always=True)
    def _initialize_queued_at(cls, v, values, **kwargs) -> timedelta:
        if v is None:
            assert values.get("mission_time") is not None
            return values.get("mission_time")
        return v
