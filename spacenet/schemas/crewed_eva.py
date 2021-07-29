from datetime import timedelta
from typing import List
from uuid import UUID

from pydantic import Field

from . import Event
from .element import HumanAgent
from .mission_demand_model import MissionDemand
from .types import SafeFloat


__all__ = [
    "CrewedEVA"
]


class EVACrew(HumanAgent):
    """
    Schema for a Crew Member
    """

    eva_state: str = Field(..., title="EVA State", description="The state of the EVA")
    # TODO: type?


class EVADemand(MissionDemand):
    """
    Schema for a Crew Member
    """

    amount: SafeFloat = Field(
        ..., title="Amount", description="The amount of the resource needed"
    )


class CrewedEVA(Event):

    name: str = Field(..., title="Name", description="Crewed EVA name")

    node_id: UUID = Field(
        ...,
        title="Origin Node ID",
        description="The origin node ID of the Space Transport",
    )

    eva_duration: timedelta = Field(
        ..., title="EVA Duration", description="The duration of the EVA"
    )

    crew_vehicle: UUID = Field(
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
