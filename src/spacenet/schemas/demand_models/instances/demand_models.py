"""Defines object schemas for instantiated demand models."""

from abc import ABC
from uuid import UUID
from typing import Union, List, Optional

from fastapi_camelcase import CamelModel
from pydantic import Field
from typing_extensions import Literal

from ...resources import (
    ResourceAmount,
    ResourceAmountRate,
    GenericResourceAmount,
    GenericResourceAmountRate,
)
from ..demand_model import DemandModelType


class InstElementDemandModel(CamelModel, ABC):
    """
    Base class for instantiated element demand models.
    """

    name: str = Field(..., title="Name", description="Instantiated demand model name")
    type: DemandModelType = Field(..., description="Demand model type")
    template_id: UUID = Field(
        ..., description="Element demand model template unique identifier"
    )


class InstMissionDemandModel(CamelModel, ABC):
    """
    Base class for instantiated mission demand models.
    """

    name: str = Field(..., title="Name", description="Instantiated demand model name")
    type: DemandModelType = Field(..., description="Demand model type")
    template_id: UUID = Field(
        ..., description="Mission demand model template unique identifier"
    )


class InstCrewConsumablesDemandModel(InstMissionDemandModel):
    """
    Instantiated mission demand model that generates demands for crew consumables.
    """

    type: Literal[DemandModelType.CREW_CONSUMABLES] = Field(
        DemandModelType.CREW_CONSUMABLES, description="Demand model type"
    )
    reserves_duration: Optional[float] = Field(
        None, title="Reserves Duration",
        description="Duration (days) of reserve resources",
        ge=0,
    )
    water_recovery_rate: Optional[float] = Field(
        None, title="Water Recovery Rate",
        description="Rate (between 0 and 1) of water recovery",
        ge=0,
        le=1,
    )
    clothing_lifetime: Optional[float] = Field(
        None, title="Clothing Lifetime",
        description="Duration (days) of clothing lifetime",
        ge=0,
    )
    transit_demands_omitted: Optional[bool] = Field(
        None, title="Transit Demand Omitted",
        description="True, if transit demands shall be omitted",
    )
    water_rate: Optional[float] = Field(
        None, title="Water Rate",
        description="Rate (kg/person/day) of water (generic COS 201) demands",
    )
    eva_water_rate: Optional[float] = Field(
        None, title="EVA Water Rate",
        description="Rate (kg/person/hour) of water (generic COS 201) demands during extra-vehicular activity",
    )
    food_support_rate: Optional[float] = Field(
        None, title="Food Support Rate",
        description="Rate (kg/person/day) of food support equipment (generic COS 202) demands",
    )
    ambient_food_rate: Optional[float] = Field(
        None, title="Ambient Food Rate",
        description="Rate (kg/person/day) of ambient food (generic COS 202) demands",
    )
    rf_food_rate: Optional[float] = Field(
        None, title="Rf Food Rate",
        description="Rate (kg/person/day) of RF food (generic COS 202) demands",
    )
    oxygen_rate: Optional[float] = Field(
        None, title="Oxygen Rate",
        description="Rate (kg/person/day) of oxygen (generic COS 203) demands",
    )
    eva_oxygen_rate: Optional[float] = Field(
        None, title="EVA Oxygen Rate",
        description="Rate (kg/person/hour) of oxygen (generic COS 203) demands during extra-vehicular activity",
    )
    nitrogen_rate: Optional[float] = Field(
        None, title="Nitrogen Rate",
        description="Rate (kg/person/day) of nitrogen (generic COS 203) demands",
    )
    hygiene_rate: Optional[float] = Field(
        None, title="Hygiene Rate",
        description="Rate (kg/person/day) of hygeine (generic COS 204) demands",
    )
    hygiene_kit: Optional[float] = Field(
        None, title="Hygiene Kit",
        description="Amount (kg/person) of hygeine kit (generic COS 204) demands",
    )
    clothing_rate: Optional[float] = Field(
        None, title="Clothing Rate",
        description="Rate (kg/person/day) of clothing (generic COS 205) demands",
    )
    personal_items: Optional[float] = Field(
        None, title="Personal Items",
        description="Amount (kg/person) of personal item (generic COS 206) demands",
    )
    office_equipment: Optional[float] = Field(
        None, title="Office Equipment",
        description="Amount (kg/person) of office equipment (generic COS 301) demands",
    )
    eva_suit: Optional[float] = Field(
        None, title="EVA Suit",
        description="Amount (kg/person) of extra-vehicular activity suit (generic COS 302) demands",
    )
    eva_lithium_hydroxide: Optional[float] = Field(
        None, title="EVA Lithium Hydroxide",
        description="Rate (kg/person/hour) of lithium hydroxide (generic COS 302) demands",
    )
    health_equipment: Optional[float] = Field(
        None, title="Health Equipment",
        description="Amount (kg) of health equipment (generic COS 303) demands",
    )
    health_consumables: Optional[float] = Field(
        None, title="Health Consumables",
        description="Amount (kg/person) of health consumables (generic COS 303) demands",
    )
    safety_equipment: Optional[float] = Field(
        None, title="Safety Equipment",
        description="Amount (kg) of safety equipment (generic COS 304) demands",
    )
    comm_equipment: Optional[float] = Field(
        None, title="Comm Equipment",
        description="Amount (kg) of communication equipment (generic COS 305) demands",
    )
    computer_equipment: Optional[float] = Field(
        None, title="Computer Equipment",
        description="Amount (kg/person) of computer equipment (generic COS 306) demands",
    )
    trash_bag_rate: Optional[float] = Field(
        None, title="Trash Bag Rate",
        description="Rate (kg/person/day) of trash bag (generic COS 701) demands",
    )
    waste_containment_rate: Optional[float] = Field(
        None, title="Waste Containment Rate",
        description="Rate (kg/person/day) of waste containment (generic COS 702) demands",
    )


class InstTimedImpulseDemandModel(InstElementDemandModel, InstMissionDemandModel):
    """
    Instantiated demand model that generates an impulsive demand for resources.
    """

    type: Literal[DemandModelType.TIMED_IMPULSE] = Field(
        DemandModelType.TIMED_IMPULSE, description="Demand model type"
    )
    demands: Optional[List[Union[ResourceAmount, GenericResourceAmount]]] = Field(
        None, description="List of resource amounts to be demanded"
    )


class InstRatedDemandModel(InstElementDemandModel, InstMissionDemandModel):
    """
    Instantiated demand model that generates a constant time rate demand for resources.
    """

    type: Literal[DemandModelType.RATED] = Field(
        DemandModelType.RATED, description="Demand model type"
    )
    demands: Optional[
        List[Union[ResourceAmountRate, GenericResourceAmountRate]]
    ] = Field(None, description="List of resource amount rates to be demanded")


class InstSparingByMassDemandModel(InstElementDemandModel):
    """
    Instantiated element demand model that generates demands for spares based on mass fraction.
    """

    type: Literal[DemandModelType.SPARING_BY_MASS] = Field(
        DemandModelType.SPARING_BY_MASS, description="Demand model type"
    )
    unpressurized_spares_rate: Optional[float] = Field(
        None, title="Unpressurized Spares Rate",
        description="Fraction of an element mass demanded per year as unpressurized spares (generic COS 4)",
    )
    pressurized_spares_rate: Optional[float] = Field(
        None, title="Pressurized Spares Rate",
        description="Fraction of an element mass demanded per year as pressurized spares (generic COS 4)",
    )
    parts_list_enabled: Optional[bool] = Field(
        None, title="Parts List Enabled",
        description="True, if the element part list identifies specific (non-generic) demands",
    )
