"""Resources define substances that can be produced or consumed during a scenario."""

from abc import ABC
from enum import Enum
from typing import Optional, Union
from uuid import UUID, uuid4

from fastapi_camelcase import CamelModel
from pydantic import Field
from typing_extensions import Literal

from .class_of_supply import ClassOfSupply
from .environment import Environment


class ResourceType(str, Enum):
    """
    An enumeration of resource types.
    """

    DISCRETE = "Discrete"
    CONTINUOUS = "Continuous"


class ResourceUUID(CamelModel):
    """
    A resource referenced by unique identifier.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique identifier")


class Resource(ResourceUUID, ABC):
    """
    A substance that can be produced, stored, and consumed during a mission.
    """

    name: str = Field(..., title="Name", description="Resource name")
    class_of_supply: ClassOfSupply = Field(
        ..., title="Class of Supply", description="Class of supply"
    )
    environment: Environment = Field(
        ..., title="Environment", description="Required stowage environment"
    )
    packing_factor: float = Field(
        ...,
        title="Packing Factor",
        description="Mass (kg) of packing material (generic COS 5) required per unit",
        ge=0,
    )
    units: str = Field(
        default="kg", title="Units", description="Unit resource label (default: kg)"
    )
    description: Optional[str] = Field(
        default=None, title="Description", description="Short description (optional)"
    )
    unit_mass: float = Field(
        ..., title="Unit Mass", description="Mass (kg) of 1.0 units", gt=0
    )
    unit_volume: float = Field(
        ..., title="Unit Volume", description="Volume (m^3) of 1.0 units", ge=0
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
