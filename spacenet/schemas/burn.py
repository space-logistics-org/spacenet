from pydantic import BaseModel, Field
from enum import Enum


class BurnType(Enum):
    """
    An enumeration of the two different types
    of burns.
    """
    OMS = "OMS"
    RCS = "RCS"


class Burn(BaseModel):
    """
    Base class for propulsive burns
    """
    edge_id: int = Field(
        ...,
        description="ID of the edge the burn will occur on",
        ge=0
    )
    time: float = Field(
        ...,
        description="Mission time at which the burn will occur",
        ge=0
   )
    order: int = Field(
        ...,
        description="Order in which this burn will occur",
        ge=0
    )
    type: BurnType = Field(
        ...,
        description="Type of propuulsive burn"
    )
    delta_v: float = Field(
        ...,
        description="Change in velocity to be achieved by a burn",
        ge=0
    )