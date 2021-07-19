from pydantic import BaseModel, Field
from enum import Enum
from typing import Dict, List, Set

from datetime import datetime

from spacenet.schemas.element import Element
from spacenet.schemas.node import Node
from spacenet.schemas.edge import Edge
from spacenet.schemas.mission import Mission

__all__ = [
    "ScenarioType",
    "Scenario",
    "Manifest"
]


class Manifest(BaseModel):
    supplyEdges: Set = Field(..., title="Supply Edges")
    supplyPoints: Set = Field(..., title="Supply Points")
    aggregatedNodeDemands: Dict = Field(..., title="Aggregated Node Demands")
    aggregatedEdgeDemands: Dict = Field(..., title="Aggregated Edge Demands")
    demandsAsPacked: Dict = Field(..., title="Demands as packed")
    packedDemands: Dict = Field(..., title="Packed Demands")
    cachedContainerDemands: Dict = Field(..., title="Cached Container Demands")
    manifestedContainers: Dict = Field(..., title="Manifested Containers")


class Network(BaseModel):
    nodes: List[Node] = Field(..., title="Nodes")
    edges: List[Edge] = Field(..., title="Edges")


class ScenarioType(str, Enum):
    iss = "ISS"
    lunar = "Lunar"
    moon_only = "Moon-only"
    martian = "Martian"
    mars_only = "Mars-only"
    solar_system = "Solar System"

    class Config:
        title: "Scenario Type"


class Scenario(BaseModel):
    name: str = Field(..., title="Name", description="Name of Scenario")
    description: str = Field(None, title="Description", description="Short description")
    startDate: datetime = Field(..., title="Start Date")
    scenarioType: ScenarioType = Field(..., title="Type of Scenario")

    network: Network = Field(..., title="Network")
    missionList: List[Mission] = Field(..., title="Mission List")
    elementList: List[Element] = Field(..., titlee="Element List")
    manifest: Manifest = Field(..., title="Manifest")

    volumeConstrained: bool = Field(False, title="Volume Constrained")
    environmentConstrained: bool = Field(False, title="Environment Constrained")

    class Config:
        title: "Scenario"
