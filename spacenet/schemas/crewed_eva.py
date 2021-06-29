from pydantic import BaseModel, Field, PositiveFloat
from typing import List
from enum import Enum


class ResourceType(str, Enum):
    """
    An enumeration for the types of edges.
    """
    generic = "Generic"
    discrete = "Discrete"
    continuous = "Continuous"


class Crew(BaseModel): 
    """
    Schema for a Crew Member
    """
    
    name = "Crew Member"
    
    eva_active: bool = Field(
        ...,
        title="EVA Active",
        description="Whether the crew member will go on the EVA"
    )
    
    eva_state: str = Field( 
        ..., 
        title= "EVA State", 
        description= "The state of the EVA"
    )
    
class Demand(BaseModel): 
    """
    Schema for Space Transport
    """
    type: ResourceType = Field(
        ...,
        title="type",
        description="Type of Resource"
    )
    
    resource: str = Field(
        ...,
        title="Resource",
        description="The object that is needed"
    )
    
    amount: PositiveFloat = Field(
        ...,
        title="Amount",
        description="The amount that is needed of the resource"
    )
    units: str = Field(
        ...,
        title="Units",
        description="The unit that the amount is expressed in"
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
    additional_demand: List[Demand] = Field( 
        ..., 
        title= "Additional Demands", 
        description = "List of demands needed for EVA"
    )
    
