from pydantic import BaseModel, Field, PositiveFloat, PositiveInt
from typing import List

from .propulsive_burn import BurnStageItem


class BurnStageSequence(BaseModel):
    burn_stage_sequence: List[BurnStageItem] = Field(
        ..., description="List of the burns and stages to be performed in the event"
    )


class SpaceTransport(BaseModel):
    """
    Schema for Space Transport
    """

    name: str = Field(..., title="Name", description="Space Transport name")

    origin_node_id: PositiveInt = Field(
        ..., title="Origin Node ID", description="The origin node Id of the Space Transport"
    )

    destination_node_id: PositiveInt = Field(
        ...,
        title="Destination Node ID",
        description="The destination node Id of the Space Transport",
    )

    time: PositiveFloat = Field(
        ...,
        title="Time",
        description="The execution time, relative to the start of the mission",
    )

    priority: int = Field(
        ..., title="Priority", description="Importance of mission event", ge=1, le=5
    )

    elements_id_list: List[PositiveInt] = Field(
        ...,
        title="Element ID List",
        description="A list of the IDs of elements that may used in the Burn-Stage Sequence",
    )

    burnStageProfile: List[BurnStageSequence] = Field(
        ..., title="Burn Sequence", description="List of seperate Burn-Stage Sequences"
    )
