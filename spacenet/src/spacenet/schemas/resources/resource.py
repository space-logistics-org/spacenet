"""Defines object schemas for resources."""

from enum import Enum
from typing import Optional, Union
from uuid import uuid4, UUID

from pydantic import Field
from typing_extensions import Literal

from ..utils import (
    ImmutableBaseModel,
    SafeNonNegFloat,
    SafePosFloat,
    ClassOfSupply,
    Environment,
)


class ResourceType(str, Enum):
    """
    An enumeration of resource types.
    """

    DISCRETE = "Discrete"
    CONTINUOUS = "Continuous"


class ResourceUUID(ImmutableBaseModel):
    """
    A resource referenced by unique identifier.

    :param UUID id: unique identifier
    """

    id: UUID = Field(default_factory=uuid4, description="Unique identifier")


class Resource(ResourceUUID):
    """
    A substance that can be produced, stored, and consumed during a mission.

    :param str name: resource name
    :param ClassOfSupply class_of_supply: class of supply
    :param Environment environment: required stowage environment
    :param SafeNonNegFloat packing_factor: mass (kg) of packing material (generic COS 5) required per unit
    :param str units: unit resource label (e.g., kg)
    :param str description: short description (optional)
    :param SafePosFloat unit_mass: mass (kg) of 1.0 units
    :param SafeNonNegFloat unit_volume: volume (m^3) of 1.0 units
    """

    name: str = Field(..., title="Name", description="Resource name")
    class_of_supply: ClassOfSupply = Field(
        ..., title="Class of Supply", description="Class of supply"
    )
    environment: Environment = Field(
        ..., title="Environment", description="Required stowage environment"
    )
    packing_factor: SafeNonNegFloat = Field(
        ...,
        title="Packing Factor",
        description="Mass (kg) of packing material (generic COS 5) required per unit",
    )
    units: str = Field(
        default="kg", title="Units", description="Unit resource label (default: kg)"
    )
    description: Optional[str] = Field(
        default=None, title="Description", description="Short description (optional)"
    )
    unit_mass: SafePosFloat = Field(
        ..., title="Unit Mass", description="Mass (kg) of 1.0 units"
    )
    unit_volume: SafeNonNegFloat = Field(
        ..., title="Unit Volume", description="Volume (m^3) of 1.0 units"
    )


class DiscreteResource(Resource):
    """
    A resource instantiated in discrete (integer) amounts.
    """

    type: Literal[ResourceType.DISCRETE] = Field(
        ResourceType.DISCRETE, title="Type", description="Resource type"
    )


class ContinuousResource(Resource):
    """
    A resource instantiated in continuous (floating point) amounts.
    """

    type: Literal[ResourceType.CONTINUOUS] = Field(
        ResourceType.CONTINUOUS, title="Type", description="Resource type"
    )


AllResources = Union[DiscreteResource, ContinuousResource]
