from pydantic import BaseModel, Field
from enum import Enum

__all__ = ["Burn", "BurnType"]


class BurnType(Enum):  # TODO: drop this? RCS too granular
    """
    An enumeration of the two different types
    of burns.
    """

    OMS = "OMS"
    RCS = "RCS"


class Burn(BaseModel):  # TODO: how does a burn decompose into RemoveElements events
    """
    Base class for propulsive burns
    """

    edge_id: int = Field(..., description="ID of the edge the burn will occur on", ge=0)
    time: float = Field(
        ..., description="Mission time at which the burn will occur", ge=0
    )
    order: int = Field(..., description="Order in which this burn will occur", ge=0)
    type: BurnType = Field(..., description="Type of propuulsive burn")
    delta_v: float = Field(
        ..., description="Change in velocity to be achieved by a burn", ge=0
    )  # TODO: how do we know the OMS delta-v of an element; you can go from delta-V and ISP
    # to fuel consumption
    # TODO: Burns should reference the IDs of elements they burn out, and those are removed
