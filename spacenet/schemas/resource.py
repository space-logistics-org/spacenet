from typing import Optional
from typing_extensions import Literal

from pydantic import BaseModel, PositiveInt, PositiveFloat, Field
from enum import Enum

from ..constants import ClassOfSupply


class ResourceType(str, Enum):
    discrete = "discrete"
    continuous = "continuous"

    class Config:
        title: "Resource Type"


class Resource(BaseModel):
    name: str = Field(..., title="Name", description="Resource name")
    cos: ClassOfSupply = Field(
        ..., title="Class of Supply", description="Class of supply number"
    )
    units: str = Field(default="kg", title="Units")
    description: Optional[str] = Field(
        default=None, title="Description", description="Short description"
    )

    class Config:
        title = "Resource Data"


class DiscreteResource(Resource):
    type: Literal[ResourceType.discrete] = Field(
        ..., title="Type", description="Resource type"
    )
    unit_mass: PositiveInt = Field(..., title="Unit Mass", description="Resource mass")
    unit_volume: PositiveInt = Field(
        ..., title="Unit Volume", description="Resource volume"
    )

    class Config:
        title = "Discrete Resource"


class ContinuousResource(Resource):
    type: Literal[ResourceType.continuous] = Field(
        ..., title="Type", description="Resource type"
    )
    unit_mass: PositiveFloat = Field(
        ..., title="Unit Mass", description="Resource mass"
    )
    unit_volume: PositiveFloat = Field(
        ..., title="Unit Volume", description="Resource volume"
    )

    class Config:
        title = "Continuous Resource"
