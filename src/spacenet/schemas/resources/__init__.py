"""Resources define substances that can be produced or consumed during a scenario."""

from typing import Union

from .class_of_supply import ClassOfSupply
from .custom import ResourceAmount, ResourceAmountRate
from .environment import Environment
from .generic import GenericResourceAmount, GenericResourceAmountRate
from .resource import (
    ContinuousResource,
    DiscreteResource,
    Resource,
    ResourceType,
    ResourceUUID,
)

AllResources = Union[ContinuousResource, DiscreteResource]
