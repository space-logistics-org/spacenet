"""Defines object schemas for resources."""

from typing import Union

from .resource import (
    ResourceType,
    ResourceUUID,
    Resource,
    ContinuousResource,
    DiscreteResource,
)
from .unique import ResourceAmount, ResourceAmountRate
from .generic import GenericResourceAmount, GenericResourceAmountRate

AllResources = Union[ContinuousResource, DiscreteResource]
