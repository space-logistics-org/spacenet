from datetime import timedelta
from uuid import UUID

from pydantic import Field
from typing import List

from spacenet.schemas import Event


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

    time: timedelta = Field(..., title="Time", description="The execution time")

    elements_id_list: List[UUID] = Field(
        ...,
        title="List of Element IDs",
        description="The list of IDs of elements being transported",
    )
