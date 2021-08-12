from typing import List, Optional
from typing_extensions import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from . import ElementTransportEvent
from .propulsive_burn import BurnStageItem


__all__ = ["SpaceTransport"]

from .types import SafeNonNegFloat


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
        description="A list of the IDs of elements that will be transported",
    )

    burnStageProfile: List[BurnStageSequence] = Field(
        ..., title="Burn Sequence", description="List of separate Burn-Stage Sequences"
    )
    type: Literal["SpaceTransport"]
    delta_v: Optional[SafeNonNegFloat] = None
