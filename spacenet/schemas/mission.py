# -*- coding: utf-8 -*-
"""
Created on Fri Jul  9 06:55:31 2021

@author: jredm
"""
from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel, Field

from .types import SafeInt
from .mission_demand_model import MissionDemand


class Mission(BaseModel):
    name: str = Field(..., title = "Name", description = "name of mission")
    start_date: datetime = Field(..., title = "Start Date", description = "date of mission start")
    events: List[SafeInt] = Field(..., title = "Event ID List", description = "list of event IDs")
    demand_models : List[MissionDemand] = Field(..., title = "Demand Models List", description = "list of mission demand models")
    origin: SafeInt = Field(..., title = "Origin ID", description = "ID of origin node")
    destination: SafeInt = Field(..., title="Destination ID", description = "ID of destination node")
    return_origin: SafeInt = Field(..., title = "Return Origin ID", description = "ID of return origin node")
    return_destination: SafeInt = Field(..., title = "Return Destination ID", description = "ID of return destination node")
