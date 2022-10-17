"""Defines object schemas for instantiated demand models."""

from abc import ABC
from uuid import UUID
from typing import Union, List, Optional

from pydantic import Field, confloat
from typing_extensions import Literal

from .demand_model import DemandModelType
from ..resources import (
    ResourceAmount,
    ResourceAmountRate,
    GenericResourceAmount,
    GenericResourceAmountRate,
)
from ..utils import ImmutableBaseModel, SafeNonNegFloat


class InstElementDemandModel(ImmutableBaseModel, ABC):
    """
    Base class for instantiated element demand models.

    :param str name: instantiated demand model name
    :param CrewConsumables type: demand model type
    :param template_id UUID: demand model template unique identifier

    """

    name: str = Field(..., title="Name", description="Instantiated demand model name")
    type: DemandModelType = Field(..., description="Demand model type")
    template_id: UUID = Field(
        ..., description="Element demand model template unique identifier"
    )


class InstMissionDemandModel(ImmutableBaseModel, ABC):
    """
    Base class for instantiated mission demand models.

    :param str name: instantiated demand model name
    :param CrewConsumables type: demand model type
    :param template_id UUID: demand model template unique identifier

    """

    name: str = Field(..., title="Name", description="Instantiated demand model name")
    type: DemandModelType = Field(..., description="Demand model type")
    template_id: UUID = Field(
        ..., description="Mission demand model template unique identifier"
    )


class InstCrewConsumablesDemandModel(InstMissionDemandModel):
    """
    Instantiated mission demand model that generates demands for crew consumables.

    :param SafeNonNegFloat reserves_duration: duration (days) of reserve resources
    :param float water_recovery_rate: rate (between 0 and 1) of water recovery
    :param SafeNonNegFloat clothing_lifetime: duration (days) of clothing lifetime
    :param bool transit_demand_omitted: True, if transit demands shall be omitted
    :param float water_rate: rate (kg/person/day) of water (generic COS 201) demands
    :param float eva_water_rate: rate (kg/person/hour) of water (generic COS 201) demands during extra-vehicular activity
    :param float food_support_rate: rate (kg/person/day) of food support equipment (generic COS 202) demands
    :param float ambient_food_rate: rate (kg/person/day) of ambient food (generic COS 202) demands
    :param float rf_food_rate: rate (kg/person/day) of refrigerated food (generic COS 202) demands
    :param float oxygen_rate: rate (kg/person/day) of oxygen (generic COS 203) demands
    :param float eva_oxygen_rate: rate (kg/person/hour) of oxygen (generic COS 203) demands during extra-vehicular activity
    :param float nitrogen_rate: rate (kg/person/day) of nitrogen (generic COS 203) demands
    :param float hygiene_rate: rate (kg/person/day) of hygeine (generic COS 204) demands
    :param float hygiene_kit: amount (kg/person) of hygeine kit (generic COS 204) demands
    :param float clothing_rate: rate (kg/person/day) of clothing (generic COS 205) demands
    :param float personal_items: amount (kg/person) of personal item (generic COS 206) demands
    :param float office_equipment: amount (kg/person) of office equipment (generic COS 301) demands
    :param float eva_suit: amount (kg/person) of extra-vehicular activity suit (generic COS 302) demands
    :param float eva_lithium_hydroxide: rate (kg/person/hour) of lithium hydroxide (generic COS 302) demands
    :param float health_equipment: amount (kg) of health equipment (generic COS 303) demands
    :param float health_consumables: amount (kg/person) of health consumables (generic COS 303) demands
    :param float safety_equipment: amount (kg) of safety equipment (generic COS 304) demands
    :param float comm_equipment: amount (kg) of communication equipment (generic COS 305) demands
    :param float computer_equipment: amount (kg/person) of computer equipment (generic COS 306) demands
    :param float trash_bag_rate: rate (kg/person/day) of trash bag (generic COS 701) demands
    :param float waste_containment_rate: rate (kg/person/day) of waste containment (generic COS 702) demands
    """

    type: Literal[DemandModelType.CREW_CONSUMABLES] = Field(
        DemandModelType.CREW_CONSUMABLES, description="Demand model type"
    )
    reserves_duration: Optional[SafeNonNegFloat] = Field(
        title="Reserves Duration", description="Duration (days) of reserve resources"
    )
    water_recovery_rate: Optional[confloat(ge=0, le=1)] = Field(
        title="Water Recovery Rate",
        description="Rate (between 0 and 1) of water recovery",
    )
    clothing_lifetime: Optional[SafeNonNegFloat] = Field(
        title="Clothing Lifetime", description="Duration (days) of clothing lifetime"
    )
    transit_demands_omitted: Optional[bool] = Field(
        title="Transit Demand Omitted",
        description="True, if transit demands shall be omitted",
    )
    water_rate: Optional[float] = Field(
        title="Water Rate",
        description="Rate (kg/person/day) of water (generic COS 201) demands",
    )
    eva_water_rate: Optional[float] = Field(
        title="EVA Water Rate",
        description="Rate (kg/person/hour) of water (generic COS 201) demands during extra-vehicular activity",
    )
    food_support_rate: Optional[float] = Field(
        title="Food Support Rate",
        description="Rate (kg/person/day) of food support equipment (generic COS 202) demands",
    )
    ambient_food_rate: Optional[float] = Field(
        title="Ambient Food Rate",
        description="Rate (kg/person/day) of ambient food (generic COS 202) demands",
    )
    rf_food_rate: Optional[float] = Field(
        title="Rf Food Rate",
        description="Rate (kg/person/day) of refrigerated food (generic COS 202) demands",
    )
    oxygen_rate: Optional[float] = Field(
        title="Oxygen Rate",
        description="Rate (kg/person/day) of oxygen (generic COS 203) demands",
    )
    eva_oxygen_rate: Optional[float] = Field(
        title="EVA Oxygen Rate",
        description="Rate (kg/person/hour) of oxygen (generic COS 203) demands during extra-vehicular activity",
    )
    nitrogen_rate: Optional[float] = Field(
        title="Nitrogen Rate",
        description="Rate (kg/person/day) of nitrogen (generic COS 203) demands",
    )
    hygiene_rate: Optional[float] = Field(
        title="Hygiene Rate",
        description="Rate (kg/person/day) of hygeine (generic COS 204) demands",
    )
    hygiene_kit: Optional[float] = Field(
        title="Hygiene Kit",
        description="Amount (kg/person) of hygeine kit (generic COS 204) demands",
    )
    clothing_rate: Optional[float] = Field(
        title="Clothing Rate",
        description="Rate (kg/person/day) of clothing (generic COS 205) demands",
    )
    personal_items: Optional[float] = Field(
        title="Personal Items",
        description="Amount (kg/person) of personal item (generic COS 206) demands",
    )
    office_equipment: Optional[float] = Field(
        title="Office Equipment",
        description="Amount (kg/person) of office equipment (generic COS 301) demands",
    )
    eva_suit: Optional[float] = Field(
        title="EVA Suit",
        description="Amount (kg/person) of extra-vehicular activity suit (generic COS 302) demands",
    )
    eva_lithium_hydroxide: Optional[float] = Field(
        title="EVA Lithium Hydroxide",
        description="Rate (kg/person/hour) of lithium hydroxide (generic COS 302) demands",
    )
    health_equipment: Optional[float] = Field(
        title="Health Equipment",
        description="Amount (kg) of health equipment (generic COS 303) demands",
    )
    health_consumables: Optional[float] = Field(
        title="Health Consumables",
        description="Amount (kg/person) of health consumables (generic COS 303) demands",
    )
    safety_equipment: Optional[float] = Field(
        title="Safety Equipment",
        description="Amount (kg) of safety equipment (generic COS 304) demands",
    )
    comm_equipment: Optional[float] = Field(
        title="Comm Equipment",
        description="Amount (kg) of communication equipment (generic COS 305) demands",
    )
    computer_equipment: Optional[float] = Field(
        title="Computer Equipment",
        description="Amount (kg/person) of computer equipment (generic COS 306) demands",
    )
    trash_bag_rate: Optional[float] = Field(
        title="Trash Bag Rate",
        description="Rate (kg/person/day) of trash bag (generic COS 701) demands",
    )
    waste_containment_rate: Optional[float] = Field(
        title="Waste Containment Rate",
        description="Rate (kg/person/day) of waste containment (generic COS 702) demands",
    )


class InstTimedImpulseDemandModel(InstElementDemandModel, InstMissionDemandModel):
    """
    Instantiated demand model that generates an impulsive demand for resources.

    :param List[Union[ResourceAmount, GenericResourceAmount]] demands: list of resource amounts to be demanded
    """

    type: Literal[DemandModelType.TIMED_IMPULSE] = Field(
        DemandModelType.TIMED_IMPULSE, description="Demand model type"
    )
    demands: Optional[List[Union[ResourceAmount, GenericResourceAmount]]] = Field(
        description="List of resource amounts to be demanded"
    )


class InstRatedDemandModel(InstElementDemandModel, InstMissionDemandModel):
    """
    Instantiated demand model that generates a constant time rate demand for resources.

    :param List[Union[ResourceAmountRate, GenericResourceAmountRate]] demands: list of resource amount rates to be demanded
    """

    type: Literal[DemandModelType.RATED] = Field(
        DemandModelType.RATED, description="Demand model type"
    )
    demands: Optional[
        List[Union[ResourceAmountRate, GenericResourceAmountRate]]
    ] = Field(description="List of resource amount rates to be demanded")


class InstSparingByMassDemandModel(InstElementDemandModel):
    """
    Instantiated element demand model that generates demands for spares based on mass fraction.

    :param float unpressurized_spares_rate: fraction of an element mass demanded per year (0 to 1 inclusive) as unpressurized spares (generic COS 4)
    :param float pressurized_spares_rate: fraction of an element mass demanded per year (0 to 1 inclusive) as pressurized spares (generic COS 4)
    :param bool parts_list_enabled: True, if the element part list identifies specific (non-generic) demands
    """

    type: Literal[DemandModelType.SPARING_BY_MASS] = Field(
        DemandModelType.SPARING_BY_MASS, description="Demand model type"
    )
    unpressurized_spares_rate: Optional[float] = Field(
        title="Unpressurized Spares Rate",
        description="Fraction of an element mass demanded per year as unpressurized spares (generic COS 4)",
    )
    pressurized_spares_rate: Optional[float] = Field(
        title="Pressurized Spares Rate",
        description="Fraction of an element mass demanded per year as pressurized spares (generic COS 4)",
    )
    parts_list_enabled: Optional[bool] = Field(
        title="Parts List Enabled",
        description="True, if the element part list identifies specific (non-generic) demands",
    )


AllInstMissionDemandModels = Union[
    InstTimedImpulseDemandModel, InstRatedDemandModel, InstCrewConsumablesDemandModel,
]
AllInstElementDemandModels = Union[
    InstTimedImpulseDemandModel, InstRatedDemandModel, InstSparingByMassDemandModel
]
AllInstDemandModels = Union[
    InstTimedImpulseDemandModel,
    InstRatedDemandModel,
    InstCrewConsumablesDemandModel,
    InstSparingByMassDemandModel,
]
