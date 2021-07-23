from datetime import timedelta
from typing import List
from uuid import UUID

from pydantic import Field

from spacenet.schemas import Event


class SurfaceTransport(Event):

    # Schema for Surface Transport

    name: str = Field(..., title="Name", description="The surface transport name")

    origin_node_id: UUID = Field(
        ...,
        title="Origin Node ID",
        description="The ID of the surface transport's origin node",
    )

    destination_node_id: UUID = Field(
        ...,
        title="Destination Node ID",
        description="The ID of the surface transport's destination node",
    )

    time: timedelta = Field(..., title="Time", description="The execution time")

    elements_id_list: List[UUID] = Field(
        ...,
        title="List of Element IDs",
        description="The list of IDs of elements being transported",
    )
