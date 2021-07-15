from pydantic import BaseModel, Field, PositiveFloat
from typing import List

from .propulsive_burn import BurnStageItem
from .element import ElementKind


class BurnStageSequence(BaseModel):
    burn_stage_sequence: List[BurnStageItem] = Field(
        ..., description="List of the burns and stages to be performed in the event"
    )


class SpaceTransport(BaseModel):
    """
    Schema for Space Transport
    """

    name: str = Field(..., title="Name", description="Space Transport name")

    # TODO
    origin_node: str = Field(  # these should be integer IDs if everything else is
        ..., title="Origin Node", description="The origin node of the Space Transport"
    )

    destination_node: str = Field(
        ...,
        title="Destination Node",
        description="The destination node of the Space Transport",
    )

    time: PositiveFloat = Field(
        ...,
        title="Time",
        description="The execution time, relative to the start of the mission",
    )

    priority: int = Field(
        ..., title="Priority", description="Importance of mission event", ge=1, le=5
    )

    elements: List[ElementKind] = Field(
        ...,
        title="Elements",
        description="The possible elements to be used in the Burn-Stage Sequence",
    )

    burnStageProfile: List[BurnStageSequence] = Field(
        ..., title="Burn Sequence", description="List of seperate Burn-Stage Sequences"
    )
