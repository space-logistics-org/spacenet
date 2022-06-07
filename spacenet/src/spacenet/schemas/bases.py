"""
This module defines base classes for events.
"""
from datetime import timedelta
from uuid import UUID
from typing import Union

from .node import NodeUUID
from .edge import EdgeUUID
from pydantic import BaseModel, Field, validator

__all__ = ["Event", "ElementTransportEvent", "PrimitiveEvent"]


class Event(BaseModel):
    """
    The base event schema.
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
    location: Union[NodeUUID, EdgeUUID] = Field(..., title="Location", description="The UUID of the node or edge at which the event begins")


class ElementTransportEvent(Event):
    """
    A schema representing a basic event transporting elements from one node to another.
    """

    edge: EdgeUUID = Field(
        ..., description="The ID of the edge between origin and destination nodes"
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
