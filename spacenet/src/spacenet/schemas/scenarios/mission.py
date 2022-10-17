"""Defines object schemas for missions."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import Field
from fastapi_camelcase import CamelModel

from ..demand_models import AllInstMissionDemandModels
from ..events import AllEvents


class Mission(CamelModel):
    """
    A mission composes a sequence of events.

    :param str name: mission name
    :param datetime start_date: time of mission start
    :param [AllEvents] events: list of events composing a mission
    :param [UUID] demand_models: list of mission demand models (by unique identifier)
    :param UUID origin: origin node unique identifier
    :param UUID destination: destination node unique identifier
    :param UUID return_origin: return origin node unique identifier (not necessary for one-way missions)
    :param UUID return_destination: return destination node unique identifier (not necessary for one-way missions)
    """

    name: str = Field(..., title="Name", description="Mission name")
    start_date: datetime = Field(
        ..., title="Start Date", description="Time of mission start"
    )
    events: List[AllEvents] = Field(
        ..., title="Event ID List", description="List of events composing a mission"
    )
    demand_models: List[AllInstMissionDemandModels] = Field(
        ...,
        title="Demand Models List",
        description="List of mission demand models (by unique identifier)",
    )
    origin: UUID = Field(
        ..., title="Origin UUID", description="Origin node unique identifier"
    )
    destination: UUID = Field(
        ..., title="Destination UUID", description="Destination node unique identifier"
    )
    return_origin: Optional[UUID] = Field(
        title="Return Origin UUID",
        description="Return origin node unique identifier (not necessary for one-way missions)",
    )
    return_destination: Optional[UUID] = Field(
        title="Return Destination ID",
        description="Return destination node unique identifier (not necessary for one-way missions)",
    )
