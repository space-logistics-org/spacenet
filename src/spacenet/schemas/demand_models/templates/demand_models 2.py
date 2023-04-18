"""Defines object schemas for demand model templates."""

from abc import ABC
from typing import List, Optional, Union
from uuid import UUID, uuid4

from fastapi_camelcase import CamelModel
from pydantic import Field
from typing_extensions import Literal

from ...resources import (
    GenericResourceAmount,
    GenericResourceAmountRate,
    ResourceAmount,
    ResourceAmountRate,
)
from ..demand_model import DemandModelType


class ElementDemandModelUUID(CamelModel):
    """
    Demand model associated with an element referenced by unique identifier.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique identifier")


class MissionDemandModelUUID(CamelModel):
    """
    Demand model associated with a mission referenced by unique idenfier.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique identifier")


class ElementDemandModel(ElementDemandModelUUID, ABC):
    """
    Abstract base class for a demand model associated with elements.
    """

    name: str = Field(..., title="Name")
    type: DemandModelType = Field(..., description="Demand model type")
    description: Optional[str] = Field(
        default=None, title="Description", description="Short description (optional)"
    )


class MissionDemandModel(MissionDemandModelUUID, ABC):
    """
    Abstract base class for a demand model associated with missions.
    """

    name: str = Field(..., title="Name")
    type: DemandModelType = Field(..., description="Demand model type")
    description: Optional[str] = Field(
        default=None, title="Description", description="Short description (optional)"
    )


class CrewConsumablesDemandModel(MissionDemandModel):
    """
    Mission demand model that generates demands for crew consumables.
    """

    type: Literal[DemandModelType.CREW_CONSUMABLES] = Field(
        DemandModelType.CREW_CONSUMABLES, description="Demand model type"
    )
    reserves_duration: float = Field(
        default=0,
        title="Reserves Duration",
        description="Duration (days) of reserve resources",
        ge=0,
    )
    water_recovery_rate: float = Field(
        default=0.42,
        title="Water Recovery Rate",
        description="Rate (between 0 and 1) of water recovery",
        ge=0,
        le=1,
    )
    clothing_lifetime: float = Field(
        default=4,
        title="Clothing Lifetime",
        description="Duration (days) of clothing lifetime",
        ge=0,
    )
    transit_demands_omitted: bool = Field(
        default=False,
        title="Transit Demand Omitted",
        description="True, if transit demands shall be omitted",
    )
    water_rate: float = Field(
        default=3.6,
        title="Water Rate",
        description="Rate (kg/person/day) of water (generic COS 201) demands",
    )
    eva_water_rate: float = Field(
        default=0.6875,
        title="EVA Water Rate",
        description="Rate (kg/person/hour) of water (generic COS 201) demands during extra-vehicular activity",
    )
    food_support_rate: float = Field(
        default=0.05556,
        title="Food Support Rate",
        description="Rate (kg/person/day) of food support equipment (generic COS 202) demands",
    )
    ambient_food_rate: float = Field(
        default=0.76389,
        title="Ambient Food Rate",
        description="Rate (kg/person/day) of ambient food (generic COS 202) demands",
    )
    rf_food_rate: float = Field(
        default=1.61667,
        title="Rf Food Rate",
        description="Rate (kg/person/day) of RF food (generic COS 202) demands",
    )
    oxygen_rate: float = Field(
        default=3.85714,
        title="Oxygen Rate",
        description="Rate (kg/person/day) of oxygen (generic COS 203) demands",
    )
    eva_oxygen_rate: float = Field(
        default=0.07875,
        title="EVA Oxygen Rate",
        description="Rate (kg/person/hour) of oxygen (generic COS 203) demands during extra-vehicular activity",
    )
    nitrogen_rate: float = Field(
        default=2.21429,
        title="Nitrogen Rate",
        description="Rate (kg/person/day) of nitrogen (generic COS 203) demands",
    )
    hygiene_rate: float = Field(
        default=0.27778,
        title="Hygiene Rate",
        description="Rate (kg/person/day) of hygeine (generic COS 204) demands",
    )
    hygiene_kit: float = Field(
        default=1.8,
        title="Hygiene Kit",
        description="Amount (kg/person) of hygeine kit (generic COS 204) demands",
    )
    clothing_rate: float = Field(
        default=2.3,
        title="Clothing Rate",
        description="Rate (kg/person/day) of clothing (generic COS 205) demands",
    )
    personal_items: float = Field(
        default=10,
        title="Personal Items",
        description="Amount (kg/person) of personal item (generic COS 206) demands",
    )
    office_equipment: float = Field(
        default=5,
        title="Office Equipment",
        description="Amount (kg/person) of office equipment (generic COS 301) demands",
    )
    eva_suit: float = Field(
        default=107,
        title="EVA Suit",
        description="Amount (kg/person) of extra-vehicular activity suit (generic COS 302) demands",
    )
    eva_lithium_hydroxide: float = Field(
        default=0.3625,
        title="EVA Lithium Hydroxide",
        description="Rate (kg/person/hour) of lithium hydroxide (generic COS 302) demands",
    )
    health_equipment: float = Field(
        default=20,
        title="Health Equipment",
        description="Amount (kg) of health equipment (generic COS 303) demands",
    )
    health_consumables: float = Field(
        default=0.1,
        title="Health Consumables",
        description="Amount (kg/person) of health consumables (generic COS 303) demands",
    )
    safety_equipment: float = Field(
        default=25,
        title="Safety Equipment",
        description="Amount (kg) of safety equipment (generic COS 304) demands",
    )
    comm_equipment: float = Field(
        default=20,
        title="Comm Equipment",
        description="Amount (kg) of communication equipment (generic COS 305) demands",
    )
    computer_equipment: float = Field(
        default=5,
        title="Computer Equipment",
        description="Amount (kg/person) of computer equipment (generic COS 306) demands",
    )
    trash_bag_rate: float = Field(
        default=0.05,
        title="Trash Bag Rate",
        description="Rate (kg/person/day) of trash bag (generic COS 701) demands",
    )
    waste_containment_rate: float = Field(
        default=0.05,
        title="Waste Containment Rate",
        description="Rate (kg/person/day) of waste containment (generic COS 702) demands",
    )


class TimedImpulseDemandModel(ElementDemandModel, MissionDemandModel):
    """
    Demand model that generates an impulsive demand for resources.
    """

    type: Literal[DemandModelType.TIMED_IMPULSE] = Field(
        DemandModelType.TIMED_IMPULSE, description="Demand model type"
    )
    demands: List[Union[ResourceAmount, GenericResourceAmount]] = Field(
        ..., description="List of resource amounts to be demanded"
    )


class RatedDemandModel(ElementDemandModel, MissionDemandModel):
    """
    Demand model that generates a constant time rate demand for resources.
    """

    type: Literal[DemandModelType.RATED] = Field(
        DemandModelType.RATED, description="Demand model type"
    )
    demands: List[Union[ResourceAmountRate, GenericResourceAmountRate]] = Field(
        ..., description="List of resource amount rates to be demanded"
    )


class SparingByMassDemandModel(ElementDemandModel):
    """
    Element demand model that generates demands for spares based on mass fraction.
    """

    type: Literal[DemandModelType.SPARING_BY_MASS] = Field(
        DemandModelType.SPARING_BY_MASS, description="Demand model type"
    )
    unpressurized_spares_rate: float = Field(
        ...,
        title="Unpressurized Spares Rate",
        description="fraction of an element mass demanded per year as unpressurized spares (generic COS 4)",
        ge=0,
        le=1,
    )
    pressurized_spares_rate: float = Field(
        ...,
        title="Pressurized Spares Rate",
        description="fraction of an element mass demanded per year as pressurized spares (generic COS 4)",
        ge=0,
        le=1,
    )
    parts_list_enabled: bool = Field(
        ...,
        title="Parts List Enabled",
        description="True, if the element part list identifies specific (non-generic) demands",
    )
