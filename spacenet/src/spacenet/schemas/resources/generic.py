"""Defines object schemas for generic resource types."""

from pydantic import Field

from ..utils import ImmutableBaseModel, ClassOfSupply, Environment


class GenericResourceAmount(ImmutableBaseModel):
    """
    A specified amount of a generic resource.

    :param ClassOfSupply class_of_supply: class of supply
    :param Environment environment: required stowage environment
    :param float amount: fixed amount of resource (kg)
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


class GenericResourceAmountRate(ImmutableBaseModel):
    """
    A specified amount of a generic resource.

    :param ClassOfSupply class_of_supply: class of supply
    :param Environment environment: required stowage environment
    :param float rate: time rate of resource (kg/day)
    """

    class_of_supply: ClassOfSupply = Field(
        ..., title="Class of Suppoly", description="Class of supply"
    )
    environment: Environment = Field(
        ..., title="Environment", description="Required stowage environment"
    )
    rate: float = Field(..., title="Rate", description="Time-rate of resource (kg/day)")
