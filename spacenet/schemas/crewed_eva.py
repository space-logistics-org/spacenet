from pydantic import BaseModel, Field, PositiveFloat
from typing import List

class Crew(BaseModel): 
    """
    Schema for a Crew Member
    """
    name = "Crew Member"
    
    node: str = Field(
        ...,
        title="Node",
        description="The location of the Crewed EVA"
    )
    
    time: PositiveFloat = Field(
        ...,
        title="Time",
        description="The execution time, relative to the start of the mission. "
    )

class CrewedEVA(BaseModel):
    """
    Schema for Space Transport
    """
    name: str = Field(
        ...,
        title="Name",
        description="Crewed EVA name"
    )
    
    node: str = Field(
        ...,
        title="Node",
        description="The location of the Crewed EVA"
    )
    
    time: PositiveFloat = Field(
        ...,
        title="Time",
        description="The execution time, relative to the start of the mission. "
    )
    
    priority: int = Field(
        ...,
        title="Priority",
        description="Importance of mission event",
        ge = 1, 
        le = 5
    )
    
    eva_duration: PositiveFloat = Field(
        ...,
        title="EVA Duration",
        description="The duraon of the EVA"
    )
    
    crew_location: str = Field( 
        ...,
        title="Crew Location",
        description="The location of the crew that will be used for the EVA"
    )
    
    crew : List[Crew] = Field(
        ..., 
        title="Crew",
        description="List of the crew selected for the EVA"
    )
