"""
This module defines an event for a single crewed extravehicular activity.
"""
from datetime import timedelta
from typing import List, Dict
from typing_extensions import Literal
from uuid import UUID

from pydantic import Field

from . import Event, EventType
from .element import HumanAgent
from .demand_model import ElementDemandModelUUID
from .types import SafeFloat
from .node import NodeUUID
from .inst_element import InstElementUUID
from .types import SafeInt


__all__ = ["CrewedEVA"]


  
class CrewedEVA(Event):
    """
    An event for a single crewed extravehicular activity.

    :param CrewedEVA type: the type of event
    :param timedelta eva_duration: the duration of the EVA
    :param UUID vehicle: the UUID of the instantiated vehicle that will be used for the EVA
    :param Dict[UUID, SafeInt] element_states: a mapping from the UUIDs of instantiated elements in the exploration to the index of their new state
    :param [UUID] additional_demands: list of UUIDs of demand models needed for EVA
    """
    type: Literal[EventType.CrewedEVA] = Field(
        EventType.CrewedEVA, title="Type", description="Type of event",
    )
    eva_duration: timedelta = Field(
        ..., title="EVA Duration", description="The duration of the EVA"
    )

    vehicle: UUID = Field(
        ...,
        title="Crew Vehicle",
        description="The UUID of the instantiated vehicle that will be used for the EVA",
    )
    element_states: Dict[UUID, SafeInt] = Field(
        ...,
        description="a mapping from the IDs of instantiated elements to the index of their desired new state",
    )
    additional_demands: List[UUID] = Field(
        ..., title="Additional Demands", description="List of UUIDs of demand models needed for EVA"
    )
