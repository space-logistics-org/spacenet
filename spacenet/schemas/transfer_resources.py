from typing import List
from uuid import UUID

from pydantic import Field

__all__ = ["TransferResourcesEvent"]

from spacenet.schemas import Event


class TransferResourcesEvent(Event):
    """
    An event that moves resources at a specific time and location (node or edge)
    from an origin resource container to a destination resource container
    """

    to_transfer: List[UUID] = Field(
        ..., description="the list of resource IDs to transfer"
    )

    origin_id: UUID = Field(
        ...,
        description="the ID of the original time and location which the "
        "resources are being transferred from",
    )

    destination_id: UUID = Field(
        ...,
        description="the ID of the new location which the elements are being transferred to",
    )
