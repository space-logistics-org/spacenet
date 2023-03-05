"""
Defines object schemas for events that act upon resources.
"""
from typing import Union
from uuid import UUID

from pydantic import Field
from typing_extensions import Literal

from .event import Event, EventType

from ..resources import ResourceAmount, GenericResourceAmount


class TransferResources(Event):
    """
    Event that transfers resources between resource container elements.
    """

    type: Literal[EventType.TRANSFER_RESOURCES] = Field(
        EventType.TRANSFER_RESOURCES,
        title="Type",
        description="Event type",
    )
    resources: Union[ResourceAmount, GenericResourceAmount] = Field(
        ...,
        title="Transferred Resources",
        description="list of resource amounts to transfer",
    )
    origin_container: UUID = Field(
        ...,
        title="Origin Container",
        description="Unique identifier of the resource-transferring origin container",
    )
    destination_container: UUID = Field(
        ...,
        title="Destination Container",
        description="Unique identifier of the resource-transferring destination container",
    )
