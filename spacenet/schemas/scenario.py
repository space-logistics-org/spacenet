from pydantic import BaseModel, Field
from enum import Enum

from datetime import datetime

from sortedcontainers import SortedDict, SortedSet

from spacenet.schemas.element import Element
from spacenet.schemas.node import Node
from spacenet.schemas.edge import Edge
# from spacenet.schemas.mission import *

__all__ = [
    "ScenarioType",
    "Scenario",
    "Manifest"
]


class Manifest(BaseModel):
    supplyEdges: SortedSet = Field(..., title="Supply Edges")
    supplyPoints: SortedSet = Field(..., title="Supply Points")
    aggregatedNodeDemands: SortedDict = Field(..., title="Aggregated Node Demands")
    aggregatedEdgeDemands: SortedDict = Field(..., title="Aggregated Edge Demands")
    demandsAsPacked: dict = Field(..., title="Demands as packed")
    packedDemands: dict = Field(..., title="Packed Demands")
    cachedContainerDemands: SortedDict = Field(..., title="Cached Container Demands")
    manifestedContainers: SortedDict = Field(..., title="Manifested Containers")

    class Config:
        arbitrary_types_allowed = True


class Network(BaseModel):
    # nodes: list[Node] = Field(..., title="Nodes")
    # edges: list[Edge] = Field(..., title="Edges")

    class Config:
        arbitrary_types_allowed = True


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
    # filePath: str = Field(..., title="File Path")
    # createdBy: str = Field(..., title="Created By")

    # dataSource: I_DataSource = Field(..., title="Data Source")

    network: Network = Field(..., title="Network")

    # missionList: list[Mission] = Field(..., title="Mission List")
        
    # elementList: list[Element] = Field(..., titlee="Element List")

    manifest: Manifest = Field(..., title="Manifest")

    # timePrecision: float = Field(..., title="Time Precision")
    # demandPrecision: float = Field(..., title="Demand Precision")
    # massPrecision: float = Field(..., title="Mass Precision")
    # volumePrecision: float = Field(..., title="Volume Precision")

    volumeConstrained: bool = Field(..., title="Volume Constrained")
    environmentConstrained: bool = Field(..., title="Environment Constrained")

    # itemDiscretization: ItemDiscretization = Field(..., title="Item Discretization")
    # itemAgrregation: float = Field(..., title="Item Aggregation")
    # scavengeSpares: bool = Field(..., title="Scavenge Spares")
    # repairedItems: dict = Field(..., title="Repaired Items")

    # detailedEva: bool = Field(..., title="Detailed EVA")
    # detailedExploration: bool = Field(..., title="Detailed Exploration")

    class Config:
        title: "Scenario"
        arbitrary_types_allowed = True
