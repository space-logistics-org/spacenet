from pydantic import BaseModel, Field, PositiveInt, PositiveFloat
from typing import List

from .propulsive_burn import BurnStageItem

class BurnStageSequence(BaseModel):
    burn_stage_sequence: List[BurnStageItem] = Field(
        ...,
        description="List of the burns and stages to be performed in the event"
    )
    
class SpaceTransport(BaseModel):
    """
    Schema for Space Transport
    """
    name: str = Field(
        ...,
        title="Name",
        description="Space Transport name"
    )
    
    node: str = Field(
        ...,
        title="Node",
        description="The origin of the Space Transport"
    )
    
    time: PositiveFloat = Field(
        ...,                                    
        title="Time",
        description="The execution time, relative to the start of the mission"
    )
    
    priority: PositiveInt = Field(
        ...,
        title="Priority",
        description="Importance of mission event",
        ge = 1, 
        le = 5
    )
    
    trajectory: str = Field(
        ...,
        title="Trajectory",
        description="The nodes that the vehicle will travel to and from"
    )
    
    elements: str = Field(
        ...,
        title="Elements",
        description="The possible elements to be used in the Burn-Stage Sequence"
    )
    
    burn_sequence: List[BurnStageSequence] = Field(
        ...,
        title="Burn Sequence",
        description="List of seperate Burn-Stage Sequences" 
    )


