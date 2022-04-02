"""
This module defines an event for a single crewed extravehicular activity.
"""
from datetime import timedelta
from typing import List
from uuid import UUID

from pydantic import Field

from . import Event
from .element import HumanAgent
from .mission_demand_model import MissionDemandUUID
from .types import SafeFloat
from .node import NodeUUID
from .element import ElementUUID


__all__ = ["CrewedEVA"]


class EVACrew(HumanAgent):
    """
    Schema for a Crew Member
    """

    eva_state: str = Field(..., title="EVA State", description="The state of the EVA")
    # TODO: type?

  
class CrewedEVA(Event):
    """
    An event for a single crewed extravehicular activity.
    """

    name: str = Field(..., title="Name", description="Crewed EVA name")

    node_id: NodeUUID = Field(
        ...,
        title="Origin Node ID",
        description="The origin node ID of the Space Transport",
    )

    eva_duration: timedelta = Field(
        ..., title="EVA Duration", description="The duration of the EVA"
    )

    crew_vehicle: ElementUUID = Field(
        ...,
        title="Crew Vehicle",
        description="The location of the crew that will be used for the EVA",
    )

    crew: List[ElementUUID] = Field(
        ..., title="Crew", description="List of the crew selected for the EVA"
    )
    additional_demand: List[MissionDemandUUID] = Field(
        ..., title="Additional Demands", description="List of demands needed for EVA"
    )
