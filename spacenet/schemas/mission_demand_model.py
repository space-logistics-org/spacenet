"""
This module defines schemas for specifying mission-wide demand models.
"""
from math import inf

from pydantic import BaseModel, Field

from .resource import Resource, ResourceType


class MissionDemand(BaseModel):
    """
    Mission Demand Model base class.
    """
    resourceType: ResourceType = Field(
        ...,
        title="Resource Type",
        description="Type of resource that is being demanded."
    )
    resource: Resource = Field(
        ...,
        title="Resource",
        description="Resource being demanded."
    )
    units: str = Field(
        ...,
        title="Units",
        description="Units of resource"
    )


class TimedModel(MissionDemand):
    """
    Timed Impulse Mission Demand Model
    A one-time demand for a set of resources scheduled for the first
    transportation arrival at the destination node.
    """
    amount: float = Field(
        ...,
        title="Amount",
        description="Amount of resource to be demanded.",
        gt=-inf,
        lt=inf,
    )


class RatedModel(MissionDemand):
    """
    Rated Demand Model
    A demand for a set of resources based on daily rates and the
    mission duration.
    """
    daily_rate: float = Field(
        ...,
        title="Daily Rate",
        description="Amount of resources to be demanded per day",
        ge=0,
        lt=inf,
    )


class ConsumablesModel(BaseModel):
    """
    Consumables Model
    A demand for resources based on NASA Space Logistics Consumables Model
    """
    mission_id: int = Field(
        ...,
        title="Mission ID",
        gt=0
    )
    reserves_duration: float = Field(
        ...,
        title="Reserves Duration",
        description="",
        gt=0,
        lt=inf,
    )
    habitat_volume: float = Field(
        ...,
        title="Habitat Volume",
        description="Volume of the habitat in cubic meters",
        gt=0,
        lt=inf,
    )
    habitat_pressure: float = Field(
        ...,
        title="Habitat Pressure",
        description="Pressure inside the habitat in absolute psi",
        gt=0,
        lt=inf,
    )
    habitat_leak_rate: float = Field(
        ...,
        title="Habitat Leak Rate",
        description="Rate of leakage in the habitat in % / day",
        ge=0,
        le=100
    )
    airlock_volume: float = Field(
        ...,
        title="Airlock Volume",
        description="Volume of the airlock in cubic meters",
        gt=0,
        lt=inf,
    )
    airlock_efficiency: float = Field(
        ...,
        title="Airlock Efficiency",
        description="Efficiency of the airlock expressed as a percentage",
        ge=0,
        le=100
    )
    waste_water_recovered: float = Field(
        ...,
        title="Waste Water Recovered",
        description="Percentage of waste water that is recovered",
        ge=0,
        le=100
    )
    solid_water_recovered: float = Field(
        ...,
        title="Solid Water Recovered",
        description="Percentage of solid water that is recovered",
        ge=0,
        le=100
    )
    brine_recycled: bool = Field(
        ...,
        title="Brine Recycled",
        description="A boolean expressing whether or not brine water is recycled"
    )
    brine_recycled_percentage: float = Field(
        ...,
        title="Brine Recycled Percentage",
        description="Percentage of brine that is recycled",
        ge=0,
        le=100
    )
    include_electrolysis: bool = Field(
        ...,
        title="Include Electrolysis",
        description="A boolean expressing whether or not to include electrolysis"
    )
    include_methane_reformer: bool = Field(
        ...,
        title="Include Methane Reformer",
        description="A boolean expressing whether or not to include methane reformer"
    )
    eva_co2_recovered: bool = Field(
        ...,
        title="EVA CO2 Recovered",
        description="A boolean expressing whether or not EVA CO2 is recovered"
    )
    include_laundry_machine: bool = Field(
        ...,
        title="Include Laundry Machine",
        description="a boolean expressing whether or not a laundry machine is included"
    )
    isru_o2_production: float = Field(
        ...,
        title="ISRU O2 Production",
        description="Amount of ISRU O2 Production in kg / year",
        gt=0,
        lt=inf,
    )
    clothes_lifetime: float = Field(
        ...,
        title="Clothes Lifetime",
        description="Number of days a piece of clothing is expected to last",
        gt=0,
        lt=inf,
    )
    press_science: float = Field(
        ...,
        title="Pressurized Science",
        description="Amount of pressurized scientific equipment in kg",
        gt=0,
        lt=inf,
    )
    unpress_science: float = Field(
        ...,
        title="Unpressurized Science",
        description="Amount of unpressurized scientific equipment in kg",
        gt=0,
        lt=inf,
    )
    transit_demands: bool = Field(
        ...,
        title="Transit Demands",
        description="A boolean expressing whether or not to incldue transit demaands"
    )