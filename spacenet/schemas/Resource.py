from pydantic import BaseModel, PositiveInt, PositiveFloat, Field
from enum import Enum

class ResourceType(str, Enum):
    discrete = "discrete"
    continuous = "continuous"
    class Config:
        title: "Resource Type"

class Resource(BaseModel):
    id: int = Field(..., description="Unique Identifier")
    name: str = Field(..., title="Name", description="Resource name")
    cos: PositiveInt = Field(..., title="Class of Supply", description="Class of supply number")
    units: str
    description: str = Field(None, title="Description", description="Short description")
    class Config:
        title = "Resource Data"

class DiscreteResource(Resource):
    type: ResourceType = Field(default=ResourceType.discrete, title="Type", description="Resource type")
    unitmass: PositiveInt = Field(..., title="Unit Mass", description="Resource mass")
    unitvolume: PositiveInt = Field(..., title="Unit Volume", description="Resource volume")
    class Config:
        title = "Discrete Resource"

class ContinuousResource(Resource):
    type: ResourceType = Field(default=ResourceType.continuous, title="Type", description="Resource type")
    unitmass: PositiveFloat = Field(..., title="Unit Mass", description="Resource mass")
    unitvolume: PositiveFloat = Field(..., title="Unit Volume", description="Resource volume")
    class Config:
        title = "Continuous Resource"
