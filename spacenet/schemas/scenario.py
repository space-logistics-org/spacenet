from datetime import datetime
from enum import Enum
from typing import Dict, List, Union
from uuid import UUID

from pydantic import BaseModel, Field

from spacenet.schemas.edge import AllUUIDEdges
from spacenet.schemas.element import AllElements
from spacenet.schemas.element_events import MakeElements, MoveElements
from spacenet.schemas.mission import Mission
from spacenet.schemas.node import AllNodes

__all__ = ["ScenarioType", "Scenario", "Manifest"]


class Manifest(BaseModel):
    container_events: List[Union[MakeElements, MoveElements]] = Field(
        ..., title="Resource Event Sequence"
    )


class Network(BaseModel):
    nodes: Dict[UUID, AllNodes] = Field(..., title="Nodes")
    edges: Dict[UUID, AllUUIDEdges] = Field(..., title="Edges")


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
    elementList: Dict[UUID, AllElements] = Field(..., title="Element List")
    manifest: Manifest = Field(..., title="Manifest")

    volumeConstrained: bool = Field(False, title="Volume Constrained")
    environmentConstrained: bool = Field(False, title="Environment Constrained")

    class Config:
        title: "Scenario"
