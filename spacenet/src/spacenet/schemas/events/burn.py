"""
Defines object schemas for propulsive burns.
"""

from enum import Enum
from typing import List
from uuid import UUID

from fastapi_camelcase import CamelModel
from pydantic import Field
from typing_extensions import Literal

from .event import Event, EventType


class BurnStage(Enum):
    """
    Enumeration of actions during a burn/stage sequence.
    """

    BURN = "Burn"
    STAGE = "Stage"


class BurnStageItem(CamelModel):
    """
    Object schema for element-specific actions during a burn/stage sequence.

    :param UUID element: unique identifier of the instantiated element performing the action
    :param BurnStage: action to be performed
    """

    element: UUID = Field(
        ...,
        title="Element",
        description="Unique identifier of the instantiated element performing the action",
    )
    type: BurnStage = Field(
        ..., title="Burn/Stage", description="Action to be performed",
    )


class PropulsiveBurn(Event):
    """
    Event that represents an impulsive propulsive maneuver composed of burn
    (fire engine) and stage (discard component) actions.

    :param [UUID] elements: list of instantiated elements (by unique identifier) to participate
    :param UUID burn: unique identifier of the burn to achieve
    :param [BurnStageItem] burn_stage_sequence: list of the actions to be sequenced
    """

    type: Literal[EventType.PROPULSIVE_BURN] = Field(
        EventType.PROPULSIVE_BURN, title="Type", description="Event type",
    )
    elements: List[UUID] = Field(
        ...,
        title="Elements List",
        description="List of instantiated elements (by unique identifier) to participate.",
    )
    burn: UUID = Field(
        ..., title="Burn", description="Unique identifier of the burn to achieve"
    )
    burn_stage_sequence: List[BurnStageItem] = Field(
        ...,
        title="Burn/Stage Sequence",
        description="List of the burns and stages to be performed in the event.",
    )
