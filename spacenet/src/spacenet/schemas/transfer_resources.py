"""
This module defines schemas for transferring resources between locations.
"""
from typing import List, Union
from uuid import UUID

from pydantic import Field
from .resource import ResourceUUID
from .bases import Event
from .node import NodeUUID
from .edge import EdgeUUID
from .inst_element import InstElementUUID

__all__ = ["TransferResources"]


class TransferResources(Event):
    """
    An event that moves resources at a specific time and location (node or edge)
    from an origin resource container to a destination resource container
    """

    resources: List[ResourceUUID] = Field(
        ..., description="the list of resource IDs to transfer"
    )

    location: Union[NodeUUID, EdgeUUID] = Field(
        ...,
        description="the UUID of the original edge or node which the "
        "resources are being transferred from",
    )

    container: Union[NodeUUID, EdgeUUID, InstElementUUID] = Field(
        ...,
        description="the UUID of the node, edge or instantiated element to which the resources are being moved",
    )
