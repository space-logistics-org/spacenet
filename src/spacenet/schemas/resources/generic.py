"""
Generic resources are substances identified by a class of supply.
"""

from fastapi_camelcase import CamelModel
from pydantic import Field

from .class_of_supply import ClassOfSupply
from .environment import Environment


class GenericResourceAmount(CamelModel):
    """
    A specified amount of a generic resource.
    """

    class_of_supply: ClassOfSupply = Field(
        ..., title="Class of Suppoly", description="Class of supply"
    )
    environment: Environment = Field(
        ..., title="Environment", description="Required stowage environment"
    )
    amount: float = Field(
        ..., title="Amount", description="Fixed amount of resource (kg)"
    )


class GenericResourceAmountRate(CamelModel):
    """
    A specified amount of a generic resource.
    """

    class_of_supply: ClassOfSupply = Field(
        ..., title="Class of Suppoly", description="Class of supply"
    )
    environment: Environment = Field(
        ..., title="Environment", description="Required stowage environment"
    )
    rate: float = Field(..., title="Rate", description="Time-rate of resource (kg/day)")
