"""
This module defines schemas for transferring resources between locations.
"""
from typing import List, Union
from typing_extensions import Literal
from uuid import UUID

from pydantic import Field
from .resource import ResourceAmount, GenericResourceAmount
from .bases import Event, EventType
from .node import NodeUUID
from .edge import EdgeUUID
from .inst_element import InstElementUUID

__all__ = ["TransferResources"]


class TransferResources(Event):
    """
    An event that moves resources at a specific time and location (node or edge)
    from an origin resource container to a destination resource container

    :param TransferResources type: type of event occurring
    :param ResourceAmount | GenericResourceAmount resources: list of resource quantities to transfer
    :param InstElementUUID container: UUID of the instantiated resource container to which the resource should be transferred
    """
    type: Literal[EventType.TransferResources] = Field(
        EventType.TransferResources, title="Type", description="Type of event",
    )
    resources: Union[ResourceAmount, GenericResourceAmount] = Field(
        ..., title="Consumed Resources", description="list of resource quantities to consume"
    )
    container: Union[NodeUUID, EdgeUUID, InstElementUUID] = Field(
        ...,
        description="the UUID of the node, edge or instantiated element to which the resources are being moved",
    )
