"""Defines object schemas for scenarios."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, confloat
from fastapi_camelcase import CamelModel

from .mission import Mission

from ..locations import AllEdges, AllNodes
from ..elements import AllElements, AllInstElements
from ..resources import AllResources
from ..demand_models import AllDemandModels
from ..utils import SafeNonNegFloat

__all__ = ["ScenarioType", "Network", "Scenario", "Manifest", "Configuration"]


class ItemDiscretizationType(str, Enum):
    """
    Enumeration of item discretization types (i.e., how discrete demands get
    aggregated to unit quantities).
    """

    DO_NOT_DISCRETIZE = "None"
    DISCRETIZE_PER_ELEMENT = "Element"
    DISCRETIZE_PER_LOCATION = "Location"
    DISCRETIZE_PER_SCENARIO = "Scenario"


class Manifest(BaseModel):
    """
    Manifest of events that schedule resource packing and loading.
    """

    pass  # TODO


class Network(BaseModel):
    """
    Composition of nodes and edges.
    """

    nodes: List[AllNodes] = Field([], title="Nodes", description="Constituent nodes")
    edges: List[AllEdges] = Field([], title="Edges", description="Constituent edges")


class Configuration(CamelModel):
    """
    Scenario configuration settings.
    """

    time_precision: SafeNonNegFloat = Field(
        0.05,
        title="Time Precision",
        description="Minimum time duration (days) considered non-zero.",
    )
    demand_precision: SafeNonNegFloat = Field(
        0.01,
        title="Demand Precision",
        description="Minimum resource amount (units) considered non-zero.",
    )
    mass_precision: SafeNonNegFloat = Field(
        0.01,
        title="Mass Precision",
        description="Minimum mass (kg) considered non-zero.",
    )
    volume_precision: SafeNonNegFloat = Field(
        1.0e-6,
        title="Volume Precision",
        description="Minimum volume (m^3) considered non-zero.",
    )
    volume_constrained: bool = Field(
        False,
        title="Volume Constrained",
        description="True, if volume constraints are enabled.",
    )
    item_discretization: ItemDiscretizationType = Field(
        ItemDiscretizationType.DO_NOT_DISCRETIZE,
        title="Item Discretization",
        description="Level at which discrete resources can be aggregated.",
    )
    item_aggregation: confloat(ge=0, le=1) = Field(
        0.0,
        title="Item Aggregation",
        description="Fraction of a unit (0 to 1 inclusive) which is aggregated to a unit demand.",
    )
    environment_constrained: bool = Field(
        False,
        title="Environment Constrained",
        description="True, if environment constraints are enabled.",
    )

    scavenge_spares: bool = Field(
        False,
        title="Scavenge Spares",
        description="True, if spares can be scavenged from parts of decommissioned elements.",
    )
    detailed_eva: bool = Field(
        True,
        title="Detailed EVA",
        description="True, if the simulator shall model all EVA events (e.g., egress, ingress).",
    )
    detailed_exploration: bool = Field(
        True,
        description="True, if the simulator shall model all exploration events (e.g., EVAs).",
    )

    generic_packing_factor_gas: SafeNonNegFloat = Field(
        1.0,
        title="Generic Gas Packing Factor",
        description="Mass of packing material (generic COS 5) required per kg of gases (generic COS 203)",
    )
    generic_packing_factor_liquid: SafeNonNegFloat = Field(
        0.5,
        title="Generic Liquid Packing Factor",
        description="Mass of packing material (generic COS 5) required per kg of liquids (generic COS 201)",
    )
    generic_packing_factor_pressurized: SafeNonNegFloat = Field(
        0.2,
        title="Generic Pressurized Packing Factor",
        description="Mass of packing material (generic COS 5) required per kg pressurized resources",
    )
    generic_packing_factor_unpressurized: SafeNonNegFloat = Field(
        0.6,
        title="Generic Unpressurized Packing Factor",
        description="Mass of packing material (generic COS 5) required per kg of unpressurized resources",
    )

    small_gas_tank_mass: SafeNonNegFloat = Field(
        10.8,
        title="Small Gas Tank Mass",
        description="Mass (kg) of small gas tank resource containers",
    )
    small_gas_tank_volume: SafeNonNegFloat = Field(
        0.275,
        title="Small Gas Tank Volume",
        description="Volume (m^3) of small gas tank resource containers",
    )
    small_gas_tank_max_mass: SafeNonNegFloat = Field(
        10.0,
        title="Small Gas Tank Max Mass",
        description="Mass capacity (kg) of small gas tank resource containers",
    )
    small_gas_t_tank_max_volume: SafeNonNegFloat = Field(
        0.275,
        title="Small Gas Tank Max Volume",
        description="Volume capacity (m^3) of small gas tank resource containers",
    )
    large_gas_tank_mass: SafeNonNegFloat = Field(
        108.0,
        title="Large Gas Tank Mass",
        description="Mass (kg) of large gas tank resource containers",
    )
    large_gas_tank_volume: SafeNonNegFloat = Field(
        2.75,
        title="Large Gas Tank Volume",
        description="Volume (m^3) of large gas tank resource containers",
    )
    large_gas_tank_max_mass: SafeNonNegFloat = Field(
        100.0,
        title="Large Gas Tank Max Mass",
        description="Mass capacity (kg) of large gas tank resource containers",
    )
    large_gas_tank_max_volume: SafeNonNegFloat = Field(
        2.75,
        title="Large Gas Tank Max Volume",
        description="Volume capacity (m^3) of large gas tank resource containers",
    )
    small_liquid_t_tank_mass: SafeNonNegFloat = Field(
        11.4567,
        title="Small Liquid Tank Mass",
        description="Mass (kg) of small liquid tank resource containers",
    )
    small_liquid_tank_volume: SafeNonNegFloat = Field(
        0.0249,
        title="Small Liquid Tank Volume",
        description="Volume (m^3) of small liquid tank resource containers",
    )
    small_liquid_tank_max_mass: SafeNonNegFloat = Field(
        24.9333,
        title="Small Liquid Tank Max Mass",
        description="Mass capacity (kg) of small liquid tank resource containers",
    )
    small_liquid_tank_max_volume: SafeNonNegFloat = Field(
        0.0249,
        title="Small Liquid Tank Max Volume",
        description="Volume capacity (m^3) of small liquid tank resource containers",
    )
    large_liquid_tank_mass: SafeNonNegFloat = Field(
        34.37,
        title="Large Liquid Tank Mass",
        description="Mass (kg) of large liquid tank resource containers",
    )
    large_liquid_tank_volume: SafeNonNegFloat = Field(
        0.0748,
        title="Large Liquid Tank Volume",
        description="Volume (m^3) of large liquid tank resource containers",
    )
    large_liquid_tank_max_mass: SafeNonNegFloat = Field(
        74.8,
        title="Large Liquid Tank Max Mass",
        description="Mass capacity (kg) of large liquid tank resource containers",
    )
    large_liquid_tank_max_volume: SafeNonNegFloat = Field(
        0.0748,
        title="Large Liquid Tank Max Volume",
        description="Volume capacity (m^3) of large liquid tank resource containers",
    )
    cargo_transfer_bag_mass: SafeNonNegFloat = Field(
        0.83,
        title="Cargo Transfer Bag Mass",
        description="Mass (kg) of cargo transfer bag resource containers",
    )
    cargo_transfer_bag_volume: SafeNonNegFloat = Field(
        0.053,
        title="Cargo Transfer Bag Volume",
        description="Volume (m^3) of cargo transfer bag resource containers",
    )
    cargo_transfer_bag_max_mass: SafeNonNegFloat = Field(
        26.8,
        title="Cargo Transfer Bag Max Mass",
        description="Mass capacity (kg) of cargo transfer bag resource containers",
    )
    cargo_transfer_bag_max_volume: SafeNonNegFloat = Field(
        0.049,
        title="Cargo Transfer Bag Max Volume",
        description="Volume capacity (m^3) of cargo transfer bag resource containers",
    )


class ScenarioType(str, Enum):
    """
    An enumeration of the different kinds of scenario.
    """

    EARTH = "Earth Only"
    LUNAR = "Lunar"
    MOON_ONLY = "Moon Only"
    MARTIAN = "Martian"
    MARS_ONLY = "Mars Only"
    SOLAR_SYSTEM = "Solar System"


class Scenario(CamelModel):
    """
    A scenario describing a space mission campaign.

    :param str name: scenario name
    :paran str created_by: scenario author
    :param str description: short description (optional)
    :param datetime start_date: time of scenario start
    :param ScenarioType scenario_type: scenario type
    :param Network network: valid locations (nodes and edges)
    :param [Mission] mission_list: list of missions
    :param [AllElements] element_templates: list of element templates
    :param [AllInstElements] instantiated_elements: list of instantiated elements
    :param [AllDemandModels] demand_models: list of demand model templates
    :param [AllResources] resource_list: list of resources used throughout the scenario
    :param Manifest manifest: object specifying packing of resources
    :param Configuration configuration: object specifying specific settings for scenario
    """

    name: str = Field(..., title="Name", description="Scenario name")
    created_by: str = Field(..., title="CreatedBy", description="Scenario author")
    description: str = Field(None, title="Description", description="Short description")
    start_date: datetime = Field(
        ..., title="Start Date", description="Time of scenario start"
    )
    scenario_type: ScenarioType = Field(
        ..., title="Type of Scenario", description="Scenario type"
    )
    network: Network = Field(
        Network(), title="Network", description="Valid locations (nodes and edges)"
    )
    mission_list: List[Mission] = Field(
        [], title="Mission List", description="List of missions"
    )
    element_templates: List[AllElements] = Field(
        [], title="Element List", description="List of element templates"
    )
    instantiated_elements: List[AllInstElements] = Field(
        [], title="Instantiated Elements", description="List of instantiated elements"
    )
    demand_models: List[AllDemandModels] = Field(
        [], title="Demand Models", description="List of demand model templates"
    )
    resource_list: List[AllResources] = Field(
        [], title="Resource List", description="List of resources"
    )
    manifest: Optional[Manifest] = Field(Manifest(), title="Manifest")
    configuration: Configuration = Field(Configuration(), title="Configuration")
