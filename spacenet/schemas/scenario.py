from pydantic import BaseModel, Field
from enum import Enum

import datetime

# from spacenet.data.I_DataSource import *
from spacenet.schemas.element. import *
# from spacenet.schemas.network import *
from spacenet.schemas.node import *
# from spacenet.simulator.event.I_Event import *
# from spacenet.util.GlobalParameters import *
from spacenet.schemas.manifest import *

class ScenarioType(str, Enum):
    iss = "ISS"
    lunar = "Lunar"
    moon_only = "Moon-only"
    martian = "Martian"
    mars_only = "Mars-only"
    solar_system = "Solar System"
    class Config:
        title: "Scenario Type"

class ItemDiscretization(str, Enum):
    none = "None"
    by_element = "Element"
    by_location = "Location"
    by_scenario = "Scenario"
    class Config:
        title: "Item Discretization"

class Scenario(BaseModel):
    name: str = Field(..., title="Name", description="Name of Scenario")
    description: str = Field(None, title="Description", description="Short description")
    startDate: datetime = Field(..., title="Start Date")
    scenarioType: ScenarioType = Field(..., title="Type of Scenario")
    filePath: str = Field(..., title="File Path")
    createdBy: str = Field(..., title="Created By")

    # dataSource: I_DataSource = Field(..., title="Data Source")

    # network: Network = Field(..., title="Network")

    missionList: list = Field(..., title="Mission List")

    manifest: Manifest = Field(..., title="Manifest")

    timePrecision: float = Field(..., title="Time Precision")
    demandPrecision: float = Field(..., title="Demand Precision")
    massPrecision: float = Field(..., title="Mass Precision")
    volumePrecision: float = Field(..., title="Volume Precision")

    volumeConstrained: bool = Field(..., title="Volume Constrained")
    environmentConstrained: bool = Field(..., title="Environment Constrained")

    itemDiscretization: ItemDiscretization = Field(..., title="Item Discretization")
    itemAgrregation: float = Field(..., title="Item Aggregation")
    scavengeSpares: bool = Field(..., title="Scavenge Spares")
    repairedItems: dict = Field(..., title="Repaired Items")

    detailedEva: bool = Field(..., title="Detailed EVA")
    detailedExploration: bool = Field(..., title="Detailed Exploration")

    class Config:
        title: "Scenario"