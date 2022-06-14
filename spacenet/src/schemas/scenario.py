"""
This module defines schemas for specifying scenarios, which describe space mission campaigns.
"""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Union
from uuid import UUID

from pydantic import BaseModel, Field

from .edge import AllEdges
from .element import AllElements
from .element_events import CreateElements, MoveElements
from .mission import Mission
from .node import AllNodes
from .resource import AllResources
from .inst_element import AllInstElements
from .demand_model import AllDemandModels
from .types import SafeNonNegFloat

__all__ = ["ScenarioType", "Scenario", "Manifest", "Configuration"]

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

class Configuration(BaseModel):
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

    small_gas_tank_mass: SafeNonNegFloat = Field(10.8)
    small_gas_tank_volume: SafeNonNegFloat = Field(0.275)
    small_gas_tank_max_mass: SafeNonNegFloat = Field(10.0)
    small_gas_tank_max_volume: SafeNonNegFloat = Field(0.275)

    large_gas_tank_mass: SafeNonNegFloat = Field(108.0)
    large_gas_tank_volume: SafeNonNegFloat = Field(2.75)
    large_gas_tank_max_mass: SafeNonNegFloat = Field(100.0)
    large_gas_tank_max_volume: SafeNonNegFloat = Field(2.75)

    small_liquid_tank_mass: SafeNonNegFloat = Field(11.4567)
    small_liquid_tank_volume: SafeNonNegFloat = Field(0.0249)
    small_liquid_tank_max_mass: SafeNonNegFloat = Field(24.9333)
    small_liquid_tank_max_volume: SafeNonNegFloat = Field(0.0249)

    large_liquid_tank_mass: SafeNonNegFloat = Field(34.37)
    large_liquid_tank_volume: SafeNonNegFloat = Field(0.0748)
    large_liquid_tank_max_mass: SafeNonNegFloat = Field(74.8)
    large_liquid_tank_max_volume: SafeNonNegFloat = Field(0.0748)

    cargo_transfer_bag_mass: SafeNonNegFloat = Field(0.83)
    cargo_transfer_bag_volume: SafeNonNegFloat = Field(0.053)
    cargo_transfer_bag_max_mass: SafeNonNegFloat = Field(26.8)
    cargo_transfer_bag_max_volume: SafeNonNegFloat = Field(0.049)

#TODO: check scenario types are accurate
class ScenarioType(str, Enum):
    """
    An enumeration of the different kinds of scenario.
    """

    earth = "Earth-only"
    lunar = "Lunar"
    moon_only = "Moon-only"
    martian = "Martian"
    mars_only = "Mars-only"
    solar_system = "Solar System"


class Scenario(BaseModel):
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
    manifest: Manifest = Field(..., title="Manifest")
    configuration: Configuration = Field(..., title="Configuration")

