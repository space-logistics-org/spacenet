"""
This module defines an event for a single crewed extravehicular activity.
"""
from datetime import timedelta
from typing import List, Dict
from uuid import UUID

from pydantic import Field

from . import Event
from .element import HumanAgent
from .element_demand_model import DemandModelUUID
from .types import SafeFloat
from .node import NodeUUID
from .inst_element import InstElementUUID
from .types import SafeInt


__all__ = ["CrewedEVA"]


class EVACrew(HumanAgent):
    """
    Schema for a Crew Member

    :param str eva_state: the state of the EVA
    """

    eva_state: str = Field(..., title="EVA State", description="The state of the EVA")
    # TODO: type?

  
class CrewedEVA(Event):
    """
    An event for a single crewed extravehicular activity.

    :param timedelta eva_duration: the duration of the EVA
    :param InstElementUUID vehicle: the UUID of the instantiated vehicle that will be used for the EVA
    :param Dict[InstElementUUID, SafeInt] crew_states: a mapping from the UUIDs of crew members in the exploration to the index number of their new state
    :param [DemandModelUUID] additional_demands: list of UUIDs of demand models needed for EVA
    """

    eva_duration: timedelta = Field(
        ..., title="EVA Duration", description="The duration of the EVA"
    )

    vehicle: InstElementUUID = Field(
        ...,
        title="Crew Vehicle",
        description="The location of the crew that will be used for the EVA",
    )
    #TODO: maps to state UUIDs or safeints?
    crew_states: Dict[InstElementUUID, SafeInt] = Field(
        ...,
        description="a mapping from the IDs of instantiated elements to the index of their desired new state",
    )
    additional_demands: List[DemandModelUUID] = Field(
        ..., title="Additional Demands", description="List of UUIDs of demand models needed for EVA"
    )