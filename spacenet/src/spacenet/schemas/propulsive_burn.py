"""
This module defines schemas for specifying propulsive maneuvers composed of at least one burn
or stage event.
"""
from enum import Enum
from typing import List
from typing_extensions import Literal
from uuid import UUID

from pydantic import BaseModel, Field, root_validator
from fastapi_camelcase import CamelModel

from . import PrimitiveEvent, EventType
from .burn import Burn
from .inst_element import InstElementUUID

__all__ = ["BurnStage", "PropulsiveBurn", "BurnStageItem"]


class BurnStage(Enum):
    """
    An enumeration of the two actions possible in a
    propulsive burn event.
    Burn - A propulsive burn,
    """

    Burn = "Burn"
    Stage = "Stage"


class BurnStageItem(CamelModel):
    """
    Class for items in the burn-stage sequence

    :param UUID element: UUID of instantiated propulsive vehicle to go through a burn or stage
    :param BurnStage: whether the target element will be burned or staged
    """

    element: UUID = Field(
        ..., title="Element", description="UUID of instantiated propulsive vehicle to go through a burn or staged"
    )
    type: BurnStage = Field(
        ...,
        title="Burn/Stage",
        description="Whether the target element will be burned or staged.",
    )


class PropulsiveBurn(PrimitiveEvent):
    """
    Event that represents a propulsive maneuver that may be composed of one or
    more burns or stages of individual elements.

    :param ProplsiveBurn type: the type of event
    :param [UUID] elements: list of UUIDs of instantiated elements to be included in the burn event
    :param UUID burn: UUID of burn upon which this event is based 
    :param [BurnStageItem] burn_stage_sequence: list of the burns and stages to be performed in the event
    
    """
    #TODO: verify burn structure
    type: Literal[EventType.PropulsiveBurn] = Field(
        EventType.PropulsiveBurn, title="Type", description="Type of event",
    )
    elements: List[UUID] = Field(
        ...,
        title="Elements List", description="List of the elements to be included in the burn event.",
    )
    burn: UUID = Field(..., title="Burn", description="UUID of burn upon which this event is based")
    burn_stage_sequence: List[BurnStageItem] = Field(
        ...,
        title="Burn/Stage Sequence",
        description="List of the burns and stages to be performed in the event.",
    )

    @root_validator(skip_on_failure=True)
    def _sequence_references_included_ids(cls, values):
        elements: List[UUID] = values.get("elements")
        assert elements is not None
        sequence: List[BurnStageItem] = values.get("burn_stage_sequence")
        assert sequence is not None
        element_set = set(elements)
        for burn_stage_item in sequence:
            assert burn_stage_item.element_id in element_set, (
                f"burn_stage_sequence involves {burn_stage_item.element_id} but "
                f"{burn_stage_item.element_id} is not included in burn event"
            )
        return values
