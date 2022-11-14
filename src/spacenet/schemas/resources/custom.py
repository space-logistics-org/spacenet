"""
Custom resources are substances identified by an underlying resource type.
"""

from uuid import UUID

from fastapi_camelcase import CamelModel
from pydantic import Field


class ResourceAmount(CamelModel):
    """
    A specified amount of a resource.
    """

    resource: UUID = Field(
        ..., title="Resource UUID", description="Resource unique identifier"
    )
    amount: float = Field(
        ..., title="Amount", description="Fixed amount of resource (units)"
    )


class ResourceAmountRate(CamelModel):
    """
    A specified amount of a resource type.
    """

    resource: UUID = Field(
        ..., title="Resource UUID", description="Resource unique identifier"
    )
    rate: float = Field(
        ..., title="Rate", description="Time-rate of resource (units/day)"
    )
