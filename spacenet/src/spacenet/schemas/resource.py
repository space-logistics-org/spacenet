"""
This module defines schemas for specifying resources.
"""
from enum import Enum
from typing import Optional

from pydantic import (
    BaseModel,
    Field,
)
from typing_extensions import Literal

from .types import SafeNonNegFloat, SafePosFloat
from .constants import ClassOfSupply

__all__ = ["ResourceType", "ContinuousResource", "DiscreteResource"]


class ResourceType(str, Enum):
    """
    An enumeration of the different kinds of resource.
    """

    Discrete = "Discrete"
    Continuous = "Continuous"


class Resource(BaseModel):
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
