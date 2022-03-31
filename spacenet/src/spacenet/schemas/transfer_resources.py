"""
This module defines schemas for transferring resources between locations.
"""
from typing import List, Union
from uuid import UUID

from pydantic import Field
from .resource import ResourceUUID
from .node import NodeUUID
from .edge import EdgeUUID

__all__ = ["TransferResources"]

from spacenet.schemas import Event


class TransferResources(Event):
    """
    An event that moves resources at a specific time and location (node or edge)
    from an origin resource container to a destination resource container
    """

    to_transfer: List[ResourceUUID] = Field(
        ..., description="the list of resource IDs to transfer"
    )

    origin_id: Union[NodeUUID, EdgeUUID] = Field(
        ...,
        description="the ID of the original time and location which the "
        "resources are being transferred from",
    )

    destination_id: Union[NodeUUID, EdgeUUID] = Field(
        ...,
        description="the ID of the new location which the elements are being transferred to",
    )
