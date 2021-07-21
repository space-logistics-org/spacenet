from datetime import timedelta
from uuid import UUID

from pydantic import BaseModel, Field, NonNegativeFloat

__all__ = ["Burn"]


class Burn(BaseModel):  # TODO: how does a burn decompose into RemoveElements events
    """
    Base class for propulsive burns
    """

    edge_id: UUID = Field(
        ..., description="ID of the edge the burn will occur on"
    )
    time: timedelta = Field(
        ..., description="Mission time at which the burn will occur"
    )
    delta_v: NonNegativeFloat = Field(
        ..., description="Change in velocity to be achieved by a burn"
    )
