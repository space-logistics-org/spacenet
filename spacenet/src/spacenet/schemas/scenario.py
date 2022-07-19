"""
This module defines schemas for specifying scenarios, which describe space mission campaigns.
"""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Union, Optional
from uuid import UUID

from pydantic import BaseModel, Field
from fastapi_camelcase import CamelModel

from .edge import AllEdges
from .element import AllElements
from .element_events import CreateElements, MoveElements
from .mission import Mission
from .node import AllNodes
from .resource import AllResources
from .inst_element import AllInstElements
from .demand_model import AllDemandModels
from .types import SafeNonNegFloat
from .constants import ClassOfSupply

__all__ = ["ScenarioType", "Network", "Scenario", "Manifest", "Configuration"]


class itemDiscretizationTypes(str, Enum):
    """
    An enumeration of all the types of item discretizations.
    """
    NoItemDiscretization = "None"
    Element = "Element"
    Location = "Location"
    Scenario = "Scenario"

class Manifest(BaseModel):
    """
    A manifest of events manipulating resources.
    """

    container_events: List[Union[CreateElements, MoveElements]] = Field(  # TODO: types?
        ..., title="Resource Event Sequence"
    )


class Network(BaseModel):
    """
    A network representation specified via nodes and edges mapped from the UUIDs which are
    used to refer to them.
    """

    nodes: List[AllNodes] = Field(..., title="Nodes")
    edges: List[AllEdges] = Field(..., title="Edges")


class Configuration(CamelModel):
    """
    The specific configuration of the scenario specifiying whether volume and environment are constrained.


    """
    time_precision: SafeNonNegFloat = Field(0.05)
    demand_precision: SafeNonNegFloat = Field(0.01)
    mass_precision: SafeNonNegFloat = Field(0.01)
    volume_precision: SafeNonNegFloat = Field(1.0E-6)
    volume_constrained: bool = Field(False, title="Volume Constrained")
    item_discretization: itemDiscretizationTypes = Field("None")
    item_aggregation: SafeNonNegFloat = Field(0.0)
    environment_constrained: bool = Field(False, title="Environment Constrained")

    scavenge_spares: bool = Field(False)
    detailed_eva: bool = Field(True)
    detailed_exploration: bool = Field(True)

    generic_packing_factor_gas: SafeNonNegFloat = Field(1.0)
    generic_packing_factor_liquid: SafeNonNegFloat = Field(0.5)
    generic_packing_factor_pressurized: SafeNonNegFloat = Field(0.2)
    generic_packing_factor_unpressurized: SafeNonNegFloat = Field(0.6)

class ScenarioType(str, Enum):
    """
    An enumeration of the different kinds of scenario.
    """

    earth = "Earth Only"
    lunar = "Lunar"
    moon_only = "Moon Only"
    martian = "Martian"
    mars_only = "Mars Only"
    solar_system = "Solar System"


class Scenario(CamelModel):
    """
    A scenario describing a space mission campaign.

    :param str name: name of the scenario
    :paran str created_by: author of the scenario
    :param str description: short description
    :param datetime start_date: start date of mission
    :param ScenarioType scenario_type: type of scenario
    :param Network network: nodes and edges used
    :param [Mission] mission_list: list of missions included in scenario
    :param [AllElements] element_templates: list of base element objects for use in scenario
    :param [AllInstElements] instantiated_elements: list of elements created in events
    :param [AllMissionDemandModels] mission_demand_models: library of mission demand models used
    :param [AllResources] resource_list: list of resources used throughout the scenario
    :param Manifest manifest: object specifying packing of resources
    :param Configuration configuration: object specifying specific settings for scenario
    """

    name: str = Field(..., title="Name", description="Name of Scenario")
    created_by: str = Field(..., title="CreatedBy", description="Author of Scenario")
    description: str = Field(None, title="Description", description="Short description")
    start_date: datetime = Field(..., title="Start Date")
    scenario_type: ScenarioType = Field(..., title="Type of Scenario")
    network: Network = Field(..., title="Network")
    mission_list: List[Mission] = Field(..., title="Mission List")
    element_templates: List[AllElements] = Field(..., title="Element List")
    instantiated_elements: List[AllInstElements] = Field(..., title="Instantiated Elements")
    demand_models: List[AllDemandModels] = Field(..., title="Demand Models")
    resource_list: List[AllResources] = Field(
        default_factory=list
    )
    manifest: Optional[Manifest] = Field(title="Manifest")
    configuration: Configuration = Field(..., title="Configuration")
