from pydantic import BaseModel, Field, PositiveFloat
from typing import List

from .mission_demand_model import MissionDemand
from .element import HumanAgent


class EVACrew(HumanAgent):
    """
    Schema for a Crew Member
    """

    eva_state: str = Field(..., title="EVA State", description="The state of the EVA")
    
class EVADemand(MissionDemand):
    """
    Schema for a Crew Member
    """

    amount: float= Field(..., title="Amount", description="The amount of the resource needed")
    
    


class CrewedEVA(BaseModel):
    """
    Schema for Space Transport
    """

    name: str = Field(..., title="Name", description="Crewed EVA name")

    type = "EVA"

    node: str = Field(
        ..., title="Origin Node", description="The origin node of the Space Transport"
    )

    time: PositiveFloat = Field(
        ...,
        title="Time",
        description="The execution time, relative to the start of the mission. ",
    )

    priority: int = Field(
        ..., title="Priority", description="Importance of mission event", ge=1, le=5
    )

    eva_duration: PositiveFloat = Field(
        ..., title="EVA Duration", description="The duraon of the EVA"
    )

    crew_vehicle: str = Field(
        ...,
        title="Crew Vehicle",
        description="The location of the crew that will be used for the EVA",
    )

    crew: List[EVACrew] = Field(
        ..., title="Crew", description="List of the crew selected for the EVA"
    )
    additional_demand: List[MissionDemand] = Field(
        ..., title="Additional Demands", description="List of demands needed for EVA"
    )
