"""
This module defines schemas for specifying scenarios, which describe space mission campaigns.
"""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Union
from uuid import UUID

from pydantic import BaseModel, Field

from spacenet.schemas.edge import AllEdges
from spacenet.schemas.element import AllElements
from spacenet.schemas.element_events import MakeElements, MoveElements
from spacenet.schemas.mission import Mission
from spacenet.schemas.node import AllNodes
from spacenet.schemas.resource import AllResources
from .inst_element import AllInstElements
from .mission_demand_model import AllMissionDemandModels

__all__ = ["ScenarioType", "Scenario", "Manifest", "Configuration"]


class Manifest(BaseModel):
    """
    A manifest of events manipulating resources.
    """

    container_events: List[Union[MakeElements, MoveElements]] = Field(  # TODO: types?
        ..., title="Resource Event Sequence"
    )


class Network(BaseModel):
    """
    A network representation specified via nodes and edges mapped from the UUIDs which are
    used to refer to them.
    """

    nodes: List[AllNodes] = Field(..., title="Nodes")
    edges: List[AllEdges] = Field(..., title="Edges")

class Configuration(BaseModel):
    """
    The specific configuration of the scenario specifiying whether volume and environment are constrained.
    """
    volumeConstrained: bool = Field(False, title="Volume Constrained")
    environmentConstrained: bool = Field(False, title="Environment Constrained")

class ScenarioType(str, Enum):
    """
    An enumeration of the different kinds of scenario.
    """

    iss = "ISS"
    lunar = "Lunar"
    moon_only = "MoonOnly"
    martian = "Martian"
    mars_only = "MarsOnly"
    solar_system = "SolarSystem"


class Scenario(BaseModel):
    """
    A scenario describing a space mission campaign.
    """

    name: str = Field(..., title="Name", description="Name of Scenario")
    description: str = Field(None, title="Description", description="Short description")
    startDate: datetime = Field(..., title="Start Date")
    scenarioType: ScenarioType = Field(..., title="Type of Scenario")
    network: Network = Field(..., title="Network")
    missionList: List[Mission] = Field(..., title="Mission List")
    elementTemplates: List[AllElements] = Field(..., title="Element List")
    instantiatedElements: List[AllInstElements]
    missionDemandModels: List[AllMissionDemandModels]
    resourceList: List[AllResources] = Field(
        default_factory=list
    )
    manifest: Manifest = Field(..., title="Manifest")
    configuration: Configuration = Field(..., title="Configuration")

