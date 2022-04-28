# -*- coding: utf-8 -*-
"""
Created on Fri Jul  9 06:55:31 2021

@author: jredm
This module defines schemas for specifying missions which compose campaigns.
"""
from datetime import datetime
from typing import List, Union
from uuid import UUID

from pydantic import BaseModel, Field

from .mission_demand_model import MissionDemandUUID
from .node import NodeUUID
from .events import (
    FlightTransport,
    SpaceTransport,
    SurfaceTransport,
    CreateElements,
    RemoveElements,
    MoveElements,
    CrewedExploration,
)

AllEvents = Union[
    FlightTransport,
    SpaceTransport,
    SurfaceTransport,
    MoveElements,
    RemoveElements,
    CreateElements,
    CrewedExploration,
]


__all__ = ["Mission"]


class Mission(BaseModel):
    """
    A schema representing a single mission, which is represented as a list of events.

    :param str name: name of mission
    :param datetime start_date: date of mission start
    :param [AllEvents] events: list of events occuring in mission
    :param [MissionDemandUUID] demand_models: list of mission demand models
    :param NodeUUID origin: UUID of origin node
    :param NodeUUID destination: UUID of destination node
    :param NodeUUID return_origin: UUID of return origin node
    :param NodeUUID return_destination: UUID of return destination node
    """

    name: str = Field(..., title="Name", description="name of mission")
    start_date: datetime = Field(
        ..., title="Start Date", description="date of mission start"
    )
    events: List[AllEvents] = Field(
        ..., title="Event ID List", description="list of events occuring in mission"
    )
    demand_models: List[MissionDemandUUID] = Field(
        ..., title="Demand Models List", description="list of mission demand models"
    )
    origin: NodeUUID = Field(..., title="Origin UUID", description="UUID of origin node")
    destination: NodeUUID = Field(
        ..., title="Destination UUID", description="UUID of destination node"
    )
    return_origin: NodeUUID = Field(
        ..., title="Return Origin UUID", description="UUID of return origin node"
    )
    return_destination: NodeUUID = Field(
        ..., title="Return Destination ID", description="ID of return destination node"
    )
