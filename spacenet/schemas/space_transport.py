from datetime import timedelta
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field

from . import ElementTransportEvent, Event
from .propulsive_burn import BurnStageItem


__all__ = ["SpaceTransport"]


class BurnStageSequence(BaseModel):
    burn_stage_sequence: List[BurnStageItem] = Field(
        ..., description="List of the burns and stages to be performed in the event"
    )


class SpaceTransport(ElementTransportEvent):
    """
    Schema for Space Transport
    """

    name: str = Field(..., title="Name", description="Space Transport name")

    elements_id_list: List[UUID] = Field(
        ...,
        title="Element ID List",
        description="A list of the IDs of elements that may used in the Burn-Stage Sequence",
    )

    burnStageProfile: List[BurnStageSequence] = Field(
        ..., title="Burn Sequence", description="List of separate Burn-Stage Sequences"
    )
