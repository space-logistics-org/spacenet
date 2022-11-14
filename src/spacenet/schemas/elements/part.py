"""
Element parts describe component resources that may fail and/or be repaired.
"""

from datetime import timedelta
from typing import Optional
from uuid import UUID

from fastapi_camelcase import CamelModel
from pydantic import Field


class Part(CamelModel):
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
    mass_to_repair: Optional[float] = Field(
        None, description="Mass (kg, generic COS 4) required to perform a repair.", ge=0
    )
    quantity: float = Field(1, description="Quantity of this part.", ge=1)
    duty_cycle: float = Field(
        1, description="Fraction of time this part is in use.", ge=0, le=1
    )
