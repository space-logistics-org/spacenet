"""
This module defines an event for a recurring crewed extravehicular activity.
"""
from datetime import timedelta
from typing import List, Union, Dict
from typing_extensions import Literal
from uuid import UUID
from pydantic import Field

from .types import SafeInt, SafeNonNegFloat, SafeNonNegInt
from .constants import SQLITE_MAX_INT
from .bases import Event, EventType
from .node import NodeUUID
from .inst_element import InstElementUUID
from .edge import EdgeUUID
from .demand_model import ElementDemandModelUUID
from .resource import ResourceAmount, GenericResourceAmount


__all__ = ["CrewedExploration"]



class CrewedExploration(Event):
    """
    Crewed Exploration Event schema

    :param timedelta eva_duration: the duration of the crewed exploration
    :param timedelta duration: the total duration of the exporation
    :param InstElementUUID vehicle: the UUID of the instantiated vehicle in which the crewed exploration will take place
    :param SafeNonNegInt eva_per_week: number of EVAs to be performed per week
    :param Dict[InstElementUUID, SafeInt] crew_states: a mapping from the UUIDs of crew members in the exploration to the index number of their new state
    :param [DemandModelUUID] additional_demands: list of UUIDs of demand models needed for EVA
    """
    type: Literal[EventType.CrewedExploration] = Field(
        EventType.CrewedExploration, title="Type", description="Type of event",
    )
    eva_duration: timedelta = Field(
        ..., title="EVA Duration", description="The duration of the crewed exploration"
    )
    duration: timedelta = Field(
        ..., title="Duration", description="The total duration of the exploration"
    )
    vehicle: UUID = Field(
        ...,
        title="Crew Vehicle",
        description="the UUID of the instantiated vehicle in which the crewed exploration will take place",
    )
    eva_per_week: SafeNonNegInt = Field(
        ...,
        title="EVAs per week",
        description="Number of EVAs to be performed a week"
    )
    element_states: Dict[InstElementUUID, SafeInt] = Field(
        ...,
        description="a mapping from the IDs of instantiated elements to the IDs of their desired "
        "new state",
    )
    additional_demands: List[Union[ResourceAmount, GenericResourceAmount]] = Field(
        ..., title="Additional Demands", description="List of additional resource quantities demanded"
    )

