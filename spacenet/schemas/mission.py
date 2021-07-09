# -*- coding: utf-8 -*-
"""
Created on Fri Jul  9 06:55:31 2021

@author: jredm
"""
from typing import Dict, List
from .types import SafeInt
from .mission_demand_model import MissionDemand
from pydantic import BaseModel, Field
from .scenario import Scenario
class Mission(BaseModel):
    name: str = Field(..., title = "Name", description = "name of mission")
    startDate: SafeInt = Field(..., title = "Start Date", description = "date of mission start")
    scenarioName: Scenario = Field(..., title = "Scenario", description = "mission scenario")
    eventList: List[SafeInt] = Field(..., title = "Event ID List", description = "list of event IDs")
    demandModels : List[MissionDemand] = Field(..., title = "Demand Models List", description = "list of mission demand models")
    destinationID: SafeInt = Field(..., title="Destination ID", description = "ID of destination node")
    originID: SafeInt = Field(..., title = "Origin ID", description = "ID of origin node")
    returnOriginID: SafeInt = Field(..., title = "Return Origin ID", description = "ID of return origin node")
    returnDestinationID: SafeInt = Field(..., title = "Return Destination ID", description = "ID of return destination node")