from uuid import UUID

from pydantic import BaseModel, Field, root_validator
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from datetime import datetime

from spacenet.schemas.element import Element
from spacenet.schemas.element_events import MakeElementsEvent, MoveElementsEvent
from spacenet.schemas.node import Node
from spacenet.schemas.edge import Edge
from spacenet.schemas.mission import Mission

__all__ = ["ScenarioType", "Scenario", "Manifest"]


class Manifest(BaseModel):
    container_events: List[Union[MakeElementsEvent, MoveElementsEvent]] = Field(
        ..., title="Resource Event Sequence"
    )


class Network(BaseModel):
    nodes: Dict[UUID, Node] = Field(..., title="Nodes")
    edges: Dict[UUID, Edge] = Field(..., title="Edges")

    @root_validator(skip_on_failure=True)
    def _no_common_ids(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        nodes = values.get("nodes")
        edges = values.get("edges")
        assert nodes is not None and edges is not None
        assert not (
            nodes.keys() & edges.keys()
        ), "must not have common ids between nodes and edges"
        return values


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
    elementList: Dict[UUID, Element] = Field(..., title="Element List")
    manifest: Manifest = Field(..., title="Manifest")

    volumeConstrained: bool = Field(False, title="Volume Constrained")
    environmentConstrained: bool = Field(False, title="Environment Constrained")

    @root_validator(skip_on_failure=True)
    def _no_common_ids(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        network: Optional[Network] = values.get("network")
        assert network is not None
        network_ids = network.nodes.keys() | network.edges.keys()
        elements = values.get("elementList")
        assert elements is not None
        assert not (
            elements.keys() & network_ids
        ), "must not have common ids between elements and network entities"
        return values

    # TODO: validator that events in missions and events in manifest agree?

    class Config:
        title: "Scenario"
