"""
This module defines a schema representing an individual burn to generate a specified amount of
velocity change.
"""
from datetime import timedelta
from uuid import UUID

from pydantic import BaseModel, Field, NonNegativeFloat
from .edge import EdgeUUID

__all__ = ["Burn"]


class Burn(BaseModel):
    """
    Base class for propulsive burns
    """

    edge_id: EdgeUUID = Field(..., description="ID of the edge the burn will occur on")
    time: timedelta = Field(
        ..., description="Mission time at which the burn will occur"
    )
    delta_v: NonNegativeFloat = Field(
        ..., description="Change in velocity to be achieved by a burn"
    )
