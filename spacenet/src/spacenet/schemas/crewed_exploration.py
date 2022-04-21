"""
This module defines an event for a recurring crewed extravehicular activity.
"""
from datetime import timedelta
from typing import List, Union
from uuid import UUID

from pydantic import Field

from .types import SafeInt, SafeNonNegFloat, SafeNonNegInt
from .constants import SQLITE_MAX_INT
from spacenet.schemas import Event
from .node import NodeUUID
from .inst_element import InstElementUUID
from .edge import EdgeUUID


__all__ = ["CrewedExploration"]


class CrewedExploration(Event):
    """
    Crewed Exploration Event schema

    :param str name: crewed exploration name
    :param NodeUUID node_id: The UUID of the node at which the crewed exploration occurs
    :param timedelta eva_duration: the duration of the crewed exploration
    :param NodeUUID | EdgeUUID crew_location: the UUID of the node or edge where the crew is located
    :param [InstElementUUID] crew: list of the crew selected for the exploration
    :param timedelta duration: the duration of the exploration
    :param NonNegInt eva_per_week: number of EVAs to be performed per week
    """

    name: str = Field(..., title="Name", description="Crewed exploration name")

    node_id: NodeUUID = Field(..., title="Node", description="The UUID of the node at which the crewed exploration occurs")

    eva_duration: timedelta = Field(
        ..., title="EVA Duration", description="The duration of the crewed exploration"
    )

    crew_location: Union[NodeUUID, EdgeUUID] = Field(
        ...,
        title="Crew Location",
        description="The location of the crew that will be used for the crewed exploration",
    )

    crew: List[InstElementUUID] = Field(
        ..., title="Crew", description="List of the crew selected for the crewed exploration"
    )
    duration: timedelta = Field(
        ...,
        title="Exploration Duration",
        description="The duration of the exploration",
    )
    eva_per_week: SafeNonNegInt = Field(
        ...,
        title="EVAs per week",
        description="Number of EVAs to be performed a week"
    )
