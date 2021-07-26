from datetime import timedelta
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field

from . import Event
from .propulsive_burn import BurnStageItem


__all__ = ["SpaceTransport"]


class BurnStageSequence(BaseModel):
    burn_stage_sequence: List[BurnStageItem] = Field(
        ..., description="List of the burns and stages to be performed in the event"
    )


class SpaceTransport(Event):
    """
    Schema for Space Transport
    """

    name: str = Field(..., title="Name", description="Space Transport name")

    origin_node_id: UUID = Field(
        ...,
        title="Origin Node ID",
        description="The origin node Id of the Space Transport",
    )

    destination_node_id: UUID = Field(
        ...,
        title="Destination Node ID",
        description="The destination node Id of the Space Transport",
    )

    exec_time: timedelta = Field(
        ..., description="The time this space transport runs for",
    )

    elements_id_list: List[UUID] = Field(
        ...,
        title="Element ID List",
        description="A list of the IDs of elements that may used in the Burn-Stage Sequence",
    )

    burnStageProfile: List[BurnStageSequence] = Field(
        ..., title="Burn Sequence", description="List of separate Burn-Stage Sequences"
    )
