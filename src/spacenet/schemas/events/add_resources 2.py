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
    """

    type: Literal[EventType.ADD_RESOURCES] = Field(
        EventType.ADD_RESOURCES,
        title="Type",
        description="Event type",
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
