# -*- coding: utf-8 -*-
"""
Created on Fri Jul  9 06:55:31 2021

@author: jredm
"""
from datetime import datetime
from typing import List, Union
from uuid import UUID

from pydantic import BaseModel, Field

from .mission_demand_model import MissionDemand
from .events import (
    FlightTransport,
    SpaceTransport,
    SurfaceTransport,
    MakeElements,
    RemoveElements,
    MoveElements,
    CrewedExploration
)

AllEvents = Union[
    FlightTransport,
    SpaceTransport,
    SurfaceTransport,
    MoveElements,
    RemoveElements,
    MakeElements,
    CrewedExploration
]  # TODO: AllEvents should be expanded to include all the types of Event


class Mission(BaseModel):  # TODO: should be UUIDs
    name: str = Field(..., title="Name", description="name of mission")
    start_date: datetime = Field(
        ..., title="Start Date", description="date of mission start"
    )
    events: List[AllEvents] = Field(
        ..., title="Event ID List", description="list of event IDs"
    )
    demand_models: List[MissionDemand] = Field(
        ..., title="Demand Models List", description="list of mission demand models"
    )
    origin: UUID = Field(..., title="Origin ID", description="ID of origin node")
    destination: UUID = Field(
        ..., title="Destination ID", description="ID of destination node"
    )
    return_origin: UUID = Field(
        ..., title="Return Origin ID", description="ID of return origin node"
    )
    return_destination: UUID = Field(
        ..., title="Return Destination ID", description="ID of return destination node"
    )
