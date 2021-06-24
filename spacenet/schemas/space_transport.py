from pydantic import BaseModel, Field, PositiveInt, PositiveFloat

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
        description="The execution time, relative to the start of the mission. "
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
        description="The elements  " ################
    )
    
    burn_sequence: dict = Field(
        ...,
        title="Burn Sequence",
        description="The execution time, relative to the start of the mission. " ###########
    )


