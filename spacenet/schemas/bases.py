from datetime import timedelta
from uuid import UUID

from pydantic import BaseModel, Field, validator

__all__ = ["Event", "ElementTransportEvent"]


class Event(BaseModel):
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
    )

    @validator("mission_time")
    def non_negative_time(cls, v):
        assert v >= timedelta(0)
        return v


class ElementTransportEvent(Event):
    origin_node_id: UUID = Field(
        ...,
        title="Origin Node ID",
        description="The ID of the transport event's origin node",
    )

    destination_node_id: UUID = Field(
        ...,
        title="Destination Node ID",
        description="The ID of the transport event's destination node",
    )

    edge_id: UUID = Field(
        ...,
        description="The ID of the edge between origin and destination nodes"
    )

    exec_time: timedelta = Field(
        ...,
        description="The time this transport event runs for"
    )
