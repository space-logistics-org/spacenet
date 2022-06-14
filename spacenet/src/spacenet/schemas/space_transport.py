"""
This module defines schemas for specifying events that transport elements through space along
edges, where the transported elements must verify they have enough fuel to provide the required
velocity change.
"""
from typing import List, Optional
from typing_extensions import Literal
from uuid import UUID

from pydantic import BaseModel, Field
from fastapi_camelcase import CamelModel

from .bases import ElementTransportEvent, EventType
from .burn import BurnUUID
from .propulsive_burn import BurnStageItem
from .inst_element import InstElementUUID
from .types import SafeNonNegFloat


__all__ = ["SpaceTransport"]




class BurnStageSequence(CamelModel):
    """
    A sequence of burn/stage events.

    :param BurnUUID burn: UUID of burn that is occurring
    :param [BurnStageItem] burn_stage_sequence: list of the burns and stages to be performed in the event
    """
    burn: UUID = Field(..., title="Burn", description="UUID of burn")
    actions: List[BurnStageItem] = Field(
        ..., description="List of the burns and stages to be performed in the event"
    )


class SpaceTransport(ElementTransportEvent):
    """
    Schema for Space Transport

    :param SpaceTransport type: type of the event
    :param [InstElementUUID] elements: list of the UUIDs of the instantiated elements that will be transported
    :param [BurnStageSequence] burn_stage_sequence: list of separate Burn-Stage sequences
    :param SafeNonNegFloat delta_v: Delta V of space transport (optional)
    """
    type: Literal[EventType.SpaceTransport] = Field(
        EventType.SpaceTransport, title="Type", description="Type of event",
    )
    elements: List[UUID] = Field(
        ...,
        title="Element ID List",
        description="A list of the UUIDs of the instantiated elements that will be transported",
    )

    burn_stage_sequence: List[BurnStageSequence] = Field(
        ..., title="Burn Sequence", description="List of separate Burn-Stage Sequences"
    )
    delta_v: Optional[SafeNonNegFloat] = None
