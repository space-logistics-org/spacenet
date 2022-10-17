"""Defines object schemas for unique resource types."""

from uuid import UUID

from pydantic import Field

from ..utils import ImmutableBaseModel


class ResourceAmount(ImmutableBaseModel):
    """
    A specified amount of a resource.

    :param UUID resource: resource unique identifier
    :param float amount: fixed amount of resource (units)
    """

    resource: UUID = Field(
        ..., title="Resource UUID", description="Resource unique identifier"
    )
    amount: float = Field(
        ..., title="Amount", description="Fixed amount of resource (units)"
    )


class ResourceAmountRate(ImmutableBaseModel):
    """
    A specified amount of a resource type.

    :param UUID resource: resource unique identifier
    :param float rate: time rate of resource (units/day)
    """

    resource: UUID = Field(
        ..., title="Resource UUID", description="Resource unique identifier"
    )
    rate: float = Field(
        ..., title="Rate", description="Time-rate of resource (units/day)"
    )
