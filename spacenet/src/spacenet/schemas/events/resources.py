"""
Defines object schemas for events that act upon resources.
"""
from typing import List, Union
from uuid import UUID

from pydantic import Field
from typing_extensions import Literal

from .event import Event, EventType

from ..resources import ResourceAmount, GenericResourceAmount


class AddResources(Event):
    """
    Event that adds resources to an instantiated container element.

    :param [ResourceAmount | GenericResourceAmount] resources: list of resource amounts to produce
    :param UUID container: unique identifier of the container element
    """

    type: Literal[EventType.ADD_RESOURCES] = Field(
        EventType.ADD_RESOURCES, title="Type", description="Event type",
    )
    resources: List[Union[ResourceAmount, GenericResourceAmount]] = Field(
        ...,
        title="Produced Resources",
        description="List of resource amounts to produce",
    )
    container: UUID = Field(
        ...,
        title="Container",
        description="Unique identifier of the container element",
    )


class ConsumeResources(Event):
    """
    Event that consumes resources.

    :param [ResourceAmount | GenericResourceAmount] resources: list of resource amounts to consume
    :param UUID source: unique identifier of the resource-consuming element
    """

    type: Literal[EventType.CONSUME_RESOURCES] = Field(
        EventType.CONSUME_RESOURCES, title="Type", description="Event type",
    )
    resources: List[Union[ResourceAmount, GenericResourceAmount]] = Field(
        ...,
        title="Consumed Resources",
        description="List of resource amounts to consume",
    )
    source: UUID = Field(
        ...,
        title="Source",
        description="Unique identifier of the resource-consuming element",
    )


class TransferResources(Event):
    """
    Event that transfers resources between resource container elements.

    :param [ResourceAmount | GenericResourceAmount] resources: list of resource amounts to transfer
    :param UUID origin: unique identifier of the resource-transferring origin container element
    :param UUID destination: unique identifier of the resource-transferring destination container element
    """

    type: Literal[EventType.TRANSFER_RESOURCES] = Field(
        EventType.TRANSFER_RESOURCES, title="Type", description="Event type",
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
