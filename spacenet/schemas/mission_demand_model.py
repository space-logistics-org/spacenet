from pydantic import BaseModel, Field, PositiveFloat
from .resource import ResourceType, Resource


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
        description="Amount of resource to be demanded."
    )


class RatedModel(MissionDemand):
    """
    Rated Demand Model
    A demand for a set of resources based on daily rates and the
    mission duration.
    """
    daily_rate: PositiveFloat = Field(
        ...,
        title="Daily Rate",
        description="Amount of resources to be demanded per day"
    )


class ConsumablesModel(BaseModel):
    """
    Consumables Model
    A demand for resources based on NASA Space Logistics Consumables Model
    """
    # TODO: Add mission field that takes a mission object schema to import certain fields

    reserves_duration: PositiveFloat = Field(
        ...,
        title="Reserves Duration",
        description=""
    )
    habitat_volume: PositiveFloat = Field(
        ...,
        title="Habitat Volume",
        description="Volume of the habitat in cubic meters"
    )
    habitat_pressure: PositiveFloat = Field(
        ...,
        title="Habitat Pressure",
        description="Pressure inside the habitat in absolute psi"
    )
    habitat_leak_rate: PositiveFloat = Field(
        ...,
        title="Habitat Leak Rate",
        description="Rate of leakage in the habitat in % / day",
        le=100
    )
    airlock_volume: PositiveFloat = Field(
        ...,
        title="Airlock Volume",
        description="Volume of the airlock in cubic meters"
    )
    airlock_efficiency: PositiveFloat = Field(
        ...,
        title="Airlock Efficiency",
        description="Efficiency of the airlock expressed as a percentage",
        le=100
    )
    waste_water_recovered: PositiveFloat = Field(
        ...,
        title="Waste Water Recovered",
        description="Percentage of waste water that is recovered",
        le=100
    )
    solid_water_recovered: PositiveFloat = Field(
        ...,
        title="Solid Water Recovered",
        description="Percentage of solid water that is recovered",
        le=100
    )
    brine_recycled: bool = Field(
        ...,
        title="Brine Recycled",
        description="A boolean expressing whether or not brine water is recycled"
    )
    brine_recycled_percentage: PositiveFloat = Field(
        ...,
        title="Brine Recycled Percentage",
        description="Percentage of brine that is recycled",
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
    isru_o2_production: PositiveFloat = Field(
        ...,
        title="ISRU O2 Production",
        description="Amount of ISRU O2 Production in kg / year"
    )
    clothes_lifetime: PositiveFloat = Field(
        ...,
        title="Clothes Lifetime",
        description="Number of days a piece of clothing is expected to last"
    )
    press_science: PositiveFloat = Field(
        ...,
        title="Pressurized Science",
        description="Amount of pressurized scientific equipment in kg"
    )
    unpress_science: PositiveFloat = Field(
        ...,
        title="Unpressurized Science",
        description="Amount of unpressurized scientific equipment in kg"
    )
    transit_demands: bool = Field(
        ...,
        title="Transit Demands",
        description="A boolean expressing whether or not to incldue transit demaands"
    )