from datetime import timedelta
from typing import List
from uuid import UUID

from pydantic import Field

from spacenet.schemas import Event


__all__ = ["FlightTransport"]


class FlightTransport(Event):

    # Schema for Flight Transport

    name: str = Field(..., title="Name", description="The flight transport name")

    origin_node_id: UUID = Field(
        ...,
        title="Origin Node ID",
        description="The ID of the flight transport's origin node",
    )

    destination_node_id: UUID = Field(
        ...,
        title="Destination Node ID",
        description="The ID of the flight transport's destination node",
    )

    exec_time: timedelta = Field(
        ..., title="Time", description="The time this flight transport runs for"
    )

    elements_id_list: List[UUID] = Field(
        ...,
        title="List of Element IDs",
        description="The list of IDs of elements being transported",
    )
