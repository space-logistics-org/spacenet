from enum import Enum
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field

from . import Event
from .burn import Burn

__all__ = ["BurnStage", "PropulsiveBurn", "BurnStageItem"]


class BurnStage(Enum):
    """
    An enumeration of the two actions possible in a
    propulsive burn event.
    Burn - A propulsive burn,
    """

    Burn = "Burn"
    Stage = "Stage"


class BurnStageItem(BaseModel):
    """
    Class for items in the burn-stage sequence
    """

    element_id: UUID = Field(
        ..., title="Element", description="Element to be burned or staged."
    )
    burnStage: BurnStage = Field(
        ...,
        title="Burn/Stage",
        description="Whether the target element will be burned or staged.",
    )


class PropulsiveBurn(Event):  # MoveElements, RemoveElements
    """
    Event that represents a propulsive maneuver that may be composed of one or
    more burns or stages of individual elements.
    """

    element_id: List[UUID] = Field(
        ...,
        title="Elements List",
        description="List of the elements to be included in the burn event.",
    )
    burn: Burn = Field(..., title="Burn", description="Burn item")
    burn_stage_sequence: List[BurnStageItem] = Field(
        ...,
        title="Burn/Stage Sequence",
        description="List of the burns and stages to be performed in the event.",
    )
