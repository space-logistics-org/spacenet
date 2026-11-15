"""Defines object schemas for manifests."""

from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi_camelcase import CamelModel
from pydantic import Field

from ..resources import ClassOfSupply, Environment

__all__ = [
    "ManifestContainerType",
    "ResourceRef",
    "SupplyEdgeRef",
    "SupplyPointRef",
    "PackedDemand",
    "ManifestContainer",
    "ManifestLoad",
    "Manifest",
]


class ManifestContainerType(str, Enum):
    """
    Enumeration of the types of logistics containers used to pack demands.
    """

    CTB = "Cargo Transfer Bag"
    HALF_CTB = "Half Cargo Transfer Bag"
    DOUBLE_CTB = "Double Cargo Transfer Bag"
    LIQUID_TANK = "Liquid Tank"
    LIQUID_TANK_DERIVATIVE = "Liquid Tank Derivative"
    GAS_TANK = "Gas Tank"
    GAS_TANK_DERIVATIVE = "Gas Tank Derivative"
    SHOSS = "Shoss"
    PRESSURIZED_SHOSS = "Pressurized Shoss"
    CUSTOM = "Custom"


class ResourceRef(CamelModel):
    """
    Reference to a resource: either a specific resource (by unique
    identifier) or a generic resource (by class of supply and environment).
    """

    resource: Optional[UUID] = Field(
        None,
        title="Resource",
        description="Unique identifier of a specific resource (undefined for a generic resource)",
    )
    class_of_supply: ClassOfSupply = Field(
        ..., title="Class of Supply", description="Class of supply"
    )
    environment: Environment = Field(
        Environment.UNPRESSURIZED,
        title="Environment",
        description="Required stowage environment",
    )


class SupplyEdgeRef(CamelModel):
    """
    Reference to a supply edge: a transport along a network edge.
    """

    edge: UUID = Field(..., title="Edge", description="Edge unique identifier")
    start_time: float = Field(
        ...,
        title="Start Time",
        description="Departure time (days) relative to the scenario start",
    )
    end_time: float = Field(
        ...,
        title="End Time",
        description="Arrival time (days) relative to the scenario start",
    )
    reversed: bool = Field(
        False,
        title="Reversed",
        description="True, if the edge is traversed from its destination to its origin",
    )


class SupplyPointRef(CamelModel):
    """
    Reference to a supply point: the arrival of a transport at a node.
    """

    node: UUID = Field(..., title="Node", description="Node unique identifier")
    time: float = Field(
        ...,
        title="Time",
        description="Arrival time (days) relative to the scenario start",
    )


class PackedDemand(CamelModel):
    """
    An amount of an aggregated demand packed in a container.
    """

    resource: ResourceRef = Field(
        ..., title="Resource", description="Demanded resource"
    )
    amount: float = Field(
        ..., title="Amount", description="Packed amount (units)", ge=0
    )
    point: SupplyPointRef = Field(
        ...,
        title="Supply Point",
        description="Supply point at which the demand is supplied",
    )
    edge_demand: Optional[SupplyEdgeRef] = Field(
        None,
        title="Edge Demand",
        description="Supply edge of a demand which occurs during a transport "
        "(undefined for a demand at a node)",
    )


class ManifestContainer(CamelModel):
    """
    A logistics container which packs demanded resources.
    """

    id: UUID = Field(default_factory=uuid4, title="ID", description="Unique identifier")
    name: str = Field(..., title="Name", description="Container name")
    container_type: ManifestContainerType = Field(
        ManifestContainerType.CUSTOM,
        title="Container Type",
        description="Type of logistics container",
    )
    mass: float = Field(0.0, title="Mass", description="Empty mass (kg)", ge=0)
    volume: float = Field(0.0, title="Volume", description="Volume (m^3)", ge=0)
    max_cargo_mass: float = Field(
        0.0, title="Max Cargo Mass", description="Cargo mass capacity (kg)", ge=0
    )
    max_cargo_volume: float = Field(
        0.0, title="Max Cargo Volume", description="Cargo volume capacity (m^3)", ge=0
    )
    environment: Environment = Field(
        Environment.UNPRESSURIZED,
        title="Environment",
        description="Required stowage environment",
    )
    cargo_environment: Environment = Field(
        Environment.UNPRESSURIZED,
        title="Cargo Environment",
        description="Stowage environment provided to contents",
    )
    contents: List[PackedDemand] = Field(
        [], title="Contents", description="Packed demands"
    )


class ManifestLoad(CamelModel):
    """
    The containers loaded in a carrier for a transport.
    """

    supply_edge: SupplyEdgeRef = Field(
        ..., title="Supply Edge", description="Transport which carries the containers"
    )
    carrier: UUID = Field(
        ..., title="Carrier", description="Unique identifier of the carrier element"
    )
    containers: List[UUID] = Field(
        [], title="Containers", description="Unique identifiers of loaded containers"
    )


class Manifest(CamelModel):
    """
    Manifest which packs demanded resources into containers and loads
    containers into the carriers of transports.
    """

    containers: List[ManifestContainer] = Field(
        [], title="Containers", description="Logistics containers"
    )
    loads: List[ManifestLoad] = Field(
        [], title="Loads", description="Containers loaded in carriers"
    )
