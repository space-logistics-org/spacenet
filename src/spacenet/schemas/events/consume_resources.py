"""
Defines object schemas for events that act upon resources.
"""
from typing import List, Union
from uuid import UUID

from pydantic import Field
from typing_extensions import Literal

from .event import Event, EventType

from ..resources import ResourceAmount, GenericResourceAmount


class ConsumeResources(Event):
    """
    Event that consumes resources.
    """

    type: Literal[EventType.CONSUME_RESOURCES] = Field(
        EventType.CONSUME_RESOURCES,
        title="Type",
        description="Event type",
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
