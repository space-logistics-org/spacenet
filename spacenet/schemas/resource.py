from typing import Optional
from typing_extensions import Literal

from pydantic import (
    BaseModel,
    NonNegativeFloat,
    NonNegativeInt,
    PositiveInt,
    PositiveFloat,
    Field,
)
from enum import Enum

from ..constants import ClassOfSupply


class ResourceType(str, Enum):
    discrete = "Discrete"
    continuous = "Continuous"


class Resource(BaseModel):
    name: str = Field(..., title="Name", description="Resource name")
    class_of_supply: ClassOfSupply = Field(
        ..., title="Class of Supply", description="Class of supply number"
    )
    units: str = Field(default="kg", title="Units")
    description: Optional[str] = Field(
        default=None, title="Description", description="Short description"
    )
    unit_mass: PositiveFloat = Field(
        ..., title="Unit Mass", description="Resource mass"
    )
    unit_volume: NonNegativeFloat = Field(
        ..., title="Unit Volume", description="Resource volume"
    )


class DiscreteResource(Resource):
    type: Literal[ResourceType.discrete] = Field(
        ..., title="Type", description="Resource type"
    )


class ContinuousResource(Resource):
    type: Literal[ResourceType.continuous] = Field(
        ..., title="Type", description="Resource type"
    )
