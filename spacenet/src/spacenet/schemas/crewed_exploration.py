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
from .state import ElementState
from .node import NodeUUID
from .inst_element import InstElementUUID
from .edge import EdgeUUID
from .demand_model import ElementDemandModelUUID
from .resource import ResourceAmount, GenericResourceAmount


__all__ = ["CrewedExploration"]



class CrewedExploration(Event):
    """
    Crewed Exploration Event schema

    :param CrewedExploration type: the type of event
    :param timedelta eva_duration: the duration of the crewed exploration
    :param timedelta duration: the total duration of the exporation
    :param tUUID vehicle: the UUID of the instantiated vehicle in which the crewed exploration will take place
    :param SafeNonNegFloat eva_per_week: number of EVAs to be performed per week
    :param List[ElementState] element_states: a list of objects specifying instantiated elements and the states to which they should be changed
    :param [UUID] additional_demands: list of UUIDs of demand models needed for EVA
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
        description="The UUID of the instantiated vehicle in which the crewed exploration will take place",
    )
    eva_per_week: SafeNonNegFloat = Field(
        ...,
        title="EVAs per week",
        description="Number of EVAs to be performed a week"
    )
    element_states: List[ElementState] = Field(
        ...,
        description="a list of objects specifying instantiated elements and the states to which they should be changed",
    )
    additional_demands: List[UUID] = Field(
        [], title="Additional Demands", description="List of UUIDs of demand models needed for EVA"
    )
