"""Defines object schemas for element parts."""

from datetime import timedelta
from typing import Optional
from uuid import UUID

from pydantic import Field, confloat

from ..utils import ImmutableBaseModel


class Part(ImmutableBaseModel):
    """
    Piece part of an element with attributes to describe failure and/or maintenance.
    """

    resource: UUID = Field(..., description="Unique identifier of resource")
    mean_time_to_failure: Optional[timedelta] = Field(
        None, description="Mean operating time to failure."
    )
    mean_time_to_repair: Optional[timedelta] = Field(
        None, description="Mean crew time to repair."
    )
    mass_to_repair: Optional[confloat(ge=0)] = Field(
        None, description="Mass (kg, generic COS 4) required to perform a repair."
    )
    quantity: confloat(ge=1) = Field(1, description="Quantity of this part.")
    duty_cycle: confloat(ge=0, le=1) = Field(
        1, description="Fraction of time this part is in use."
    )
