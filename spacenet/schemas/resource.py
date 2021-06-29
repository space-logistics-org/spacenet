from math import inf
from typing import Optional
from typing_extensions import Literal

from pydantic import (
    BaseModel,
    Field,
    confloat,
)
from enum import Enum

from ..constants import ClassOfSupply

__all__ = ["ResourceType", "ContinuousResource", "DiscreteResource"]


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
    unit_mass: confloat(gt=0, lt=inf) = Field(
        ..., title="Unit Mass", description="Resource mass"
    )
    unit_volume: confloat(ge=0, lt=inf) = Field(
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
