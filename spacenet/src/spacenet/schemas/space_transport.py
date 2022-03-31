"""
This module defines schemas for specifying events that transport elements through space along
edges, where the transported elements must verify they have enough fuel to provide the required
velocity change.
"""
from typing import List, Optional
from typing_extensions import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from .bases import ElementTransportEvent
from .propulsive_burn import BurnStageItem
from .inst_element import InstElementUUID


__all__ = ["SpaceTransport"]

from .types import SafeNonNegFloat


class BurnStageSequence(BaseModel):
    """
    A sequence of burn/stage events.
    """

    burn_stage_sequence: List[BurnStageItem] = Field(
        ..., description="List of the burns and stages to be performed in the event"
    )


class SpaceTransport(ElementTransportEvent):
    """
    Schema for Space Transport
    """

    elements: List[InstElementUUID] = Field(
        ...,
        title="Element ID List",
        description="A list of the UUIDs of the instantiated elements that will be transported",
    )

    burnStageProfile: List[BurnStageSequence] = Field(
        ..., title="Burn Sequence", description="List of separate Burn-Stage Sequences"
    )
    type: Literal["SpaceTransport"]
    delta_v: Optional[SafeNonNegFloat] = None
