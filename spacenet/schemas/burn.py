from datetime import timedelta
from uuid import UUID

from pydantic import BaseModel, Field, NonNegativeFloat

__all__ = ["Burn"]


class Burn(BaseModel):
    """
    Base class for propulsive burns
    """

    edge_id: UUID = Field(
        ..., description="ID of the edge the burn will occur on", ge=0
    )
    time: timedelta = Field(
        ..., description="Mission time at which the burn will occur", ge=0
    )
    delta_v: NonNegativeFloat = Field(
        ..., description="Change in velocity to be achieved by a burn"
    )
