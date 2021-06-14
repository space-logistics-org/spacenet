from pydantic import BaseModel, PositiveInt, PositiveFloat, Field
from enum import Enum

from ..constants import ClassOfSupply


class ResourceType(str, Enum):
    discrete = "discrete"
    continuous = "continuous"

    class Config:
        title: "Resource Type"


class Resource(BaseModel):
    id: int = Field(..., description="Unique Identifier")
    name: str = Field(..., title="Name", description="Resource name")
    cos: ClassOfSupply = Field(
        ..., title="Class of Supply", description="Class of supply number"
    )
    units: str = Field(default="kg", title="Units")
    description: str = Field(None, title="Description", description="Short description")

    class Config:
        title = "Resource Data"


class DiscreteResource(Resource):
    type: ResourceType = Field(
        default=ResourceType.discrete, title="Type", description="Resource type"
    )
    unit_mass: PositiveInt = Field(..., title="Unit Mass", description="Resource mass")
    unit_volume: PositiveInt = Field(
        ..., title="Unit Volume", description="Resource volume"
    )

    class Config:
        title = "Discrete Resource"


class ContinuousResource(Resource):
    type: ResourceType = Field(
        default=ResourceType.continuous, title="Type", description="Resource type"
    )
    unit_mass: PositiveFloat = Field(
        ..., title="Unit Mass", description="Resource mass"
    )
    unit_volume: PositiveFloat = Field(
        ..., title="Unit Volume", description="Resource volume"
    )

    class Config:
        title = "Continuous Resource"
