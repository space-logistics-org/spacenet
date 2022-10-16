# -*- coding: utf-8 -*-
"""
Created on Fri Jul  9 06:55:31 2021

@author: jredm
This module defines schemas for specifying missions which compose campaigns.
"""
from datetime import datetime
from typing import List, Union, Optional
from uuid import UUID

from pydantic import BaseModel, Field
from fastapi_camelcase import CamelModel

from .inst_demand_model import AllInstMissionDemandModels
from .node import NodeUUID
from .events import *

AllEvents = Union[
    FlightTransport,
    SpaceTransport,
    SurfaceTransport,
    MoveElements,
    RemoveElements,
    CreateElements,
    CrewedExploration,
    ConsumeResources,
    ReconfigureElements,
    ReconfigureElement
]


__all__ = ["Mission"]


class Mission(CamelModel):
    """
    A schema representing a single mission, which is represented as a list of events.

    :param str name: name of mission
    :param datetime start_date: date of mission start
    :param [AllEvents] events: list of events occuring in mission
    :param [UUID] demand_models: list of mission demand models by UUID
    :param UUID origin: UUID of origin node
    :param UUID destination: UUID of destination node
    :param UUID return_origin: UUID of return origin node (not necessary for one-way missions)
    :param UUID return_destination: UUID of return destination node (not necessary for one-way missions)
    """

    name: str = Field(..., title="Name", description="name of mission")
    start_date: datetime = Field(
        ..., title="Start Date", description="date of mission start"
    )
    events: List[AllEvents] = Field(
        ..., title="Event ID List", description="list of events occuring in mission"
    )
    demand_models: List[AllInstMissionDemandModels] = Field(
        ..., title="Demand Models List", description="list of mission demand models by UUID"
    )
    origin: UUID = Field(..., title="Origin UUID", description="UUID of origin node")
    destination: UUID = Field(
        ..., title="Destination UUID", description="UUID of destination node"
    )
    return_origin: Optional[UUID] = Field(
        title="Return Origin UUID", description="UUID of return origin node (not necessary for one-way missions)"
    )
    return_destination: Optional[UUID] = Field(
        title="Return Destination ID", description="ID of return destination node (not necessary for one-way missions"
    )
