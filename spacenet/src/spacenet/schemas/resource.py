"""
This module defines schemas for specifying resources.
"""
from enum import Enum
from typing import List, Optional, Union
from uuid import uuid4, UUID

from pydantic import (
    BaseModel,
    Field,
)
from typing_extensions import Literal

from .mixins import ImmutableBaseModel
from .types import SafeNonNegFloat, SafePosFloat
from .constants import ClassOfSupply

__all__ = ["ResourceType", "ContinuousResource", "DiscreteResource", "ResourceUUID", "Resource"]

class ResourceUUID(ImmutableBaseModel):
    """
    A base class which defines a resource by its UUID only.
    """
    id: UUID = Field(default_factory=uuid4, description="unique identifier for resource")


class ResourceType(str, Enum):
    """
    An enumeration of the different kinds of resource.
    """

    Discrete = "Discrete"
    Continuous = "Continuous"


class Resource(ResourceUUID):
    """
    A resource with a given class of supply as a general category, as well as specified
    physical properties such as mass and volume.
    """

    name: str = Field(..., title="Name", description="Resource name")
    class_of_supply: ClassOfSupply = Field(
        ..., title="Class of Supply", description="Class of supply number"
    )
    units: str = Field(default="kg", title="Units")
    description: Optional[str] = Field(
        default=None, title="Description", description="Short description"
    )
    unit_mass: SafePosFloat = Field(..., title="Unit Mass", description="Resource mass")
    unit_volume: SafeNonNegFloat = Field(
        ..., title="Unit Volume", description="Resource volume"
    )


class DiscreteResource(Resource):
    """
    A resource which can only be replaced in discrete increments.
    """

    type: Literal[ResourceType.Discrete] = Field(
        ..., title="Type", description="Resource type"
    )


class ContinuousResource(Resource):
    """
    A resource which can be replaced in continuous increments.
    """

    type: Literal[ResourceType.Continuous] = Field(
        ..., title="Type", description="Resource type"
    )

AllResources = Union[DiscreteResource, ContinuousResource]
