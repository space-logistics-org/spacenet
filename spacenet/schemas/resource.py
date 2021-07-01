from typing import Optional
from typing_extensions import Literal

from pydantic import (
    BaseModel,
    Field,
)
from enum import Enum

from .types import SafeNonNegFloat, SafePosFloat
from ..constants import ClassOfSupply

__all__ = ["ResourceType", "ContinuousResource", "DiscreteResource"]


class ResourceType(str, Enum):
    Discrete = "Discrete"
    Continuous = "Continuous"


class Resource(BaseModel):
    name: str = Field(..., title="Name", description="Resource name")
    class_of_supply: ClassOfSupply = Field(
        ..., title="Class of Supply", description="Class of supply number"
    )
    units: str = Field(default="kg", title="Units")
    description: Optional[str] = Field(
        default=None, title="Description", description="Short description"
    )
    unit_mass: SafePosFloat = Field(
        ..., title="Unit Mass", description="Resource mass"
    )
    unit_volume: SafeNonNegFloat = Field(
        ..., title="Unit Volume", description="Resource volume"
    )


class DiscreteResource(Resource):
    type: Literal[ResourceType.Discrete] = Field(
        ..., title="Type", description="Resource type"
    )


class ContinuousResource(Resource):
    type: Literal[ResourceType.Continuous] = Field(
        ..., title="Type", description="Resource type"
    )
