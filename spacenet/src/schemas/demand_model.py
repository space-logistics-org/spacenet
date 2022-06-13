"""
This module defines schemas for specifying mission-wide demand models.
"""
from math import inf
from uuid import uuid4, UUID
from typing import Union, List
from enum import Enum

from pydantic import BaseModel, Field
from typing_extensions import Literal
from .mixins import ImmutableBaseModel

from .resource import ResourceAmount, ResourceAmountRate, GenericResourceAmount, GenericResourceAmountRate
from .mixins import ImmutableBaseModel


__all__ = [
    "MissionDemandModelUUID",
    "ElementDemandModelUUID",
    "TimedImpulseDemandModel",
    "RatedDemandModel",
    "CrewConsumablesDemandModel",
    "AllDemandModels"
]

#TODO: is this structure possible?
class DemandModelKind(str, Enum):
    """
    An enumeration of all the types of Demand Model.
    """
    CrewConsumables = "Crew Consumables"
    TimedImpulse = "Timed Impulse"
    Rated = "Rated"
    SparingByMass = "Sparing By Mass"

class ElementDemandModelUUID(ImmutableBaseModel):
    """
    A representation of an element demand model containing only its UUID and serving as a base class for all other demand models.

    :param UUID id: unique identifier for element demand model
    """
    id: UUID = Field(default_factory=uuid4, description="unique identifier for demand model")

class MissionDemandModelUUID(ImmutableBaseModel):
    """
    A representation of a mission demand model containing only its UUID and serving as a base class for all other demand models.

    :param UUID id: unique identifier for element demand model
    """
    id: UUID = Field(default_factory=uuid4, description="unique identifier for demand model")


class ElementDemandModel(ElementDemandModelUUID):
    """
    Element Demand Model base class.

    :param str name: name of demand model
    """
    name: str = Field(..., title="Name")

class MissionDemandModel(MissionDemandModelUUID):
    """
    Mission Demand Model base class.

    :param str name: name of demand model
    """
    name: str = Field(..., title="Name")

class CrewConsumablesDemandModel(MissionDemandModel):
    """
    Demands for consumables by crew.

    :param CrewConsumables type: 
    :param float reserves_duration: 
    :param float water_recovery_rate: 
    :param float clothing_lifetime: 
    :param float transit_demand_omitted: 
    :param float water_rate: 
    :param float eva_water_rate: 
    :param float food_support_rate: 
    :param float ambient_food_rate: 
    :param float rf_food_rate: 
    :param float oxygen_rate: 
    :param float eva_oxygen_rate: 
    :param float nitrogen_rate: 
    :param float hygiene_rate: 
    :param float hygiene_kit: 
    :param float clothing_rate: 
    :param float personal_items: 
    :param float office_equipment: 
    :param float eva_suit: 
    :param float eva_lithium_hydroxide: 
    :param float health_equipment: 
    :param float health_consumables: 
    :param float safety_equipment: 
    :param float comm_equipment: 
    :param float computer_equipment: 
    :param float trash_bag_rate: 
    :param float waste_containment_rate: 
    """
    type: Literal[DemandModelKind.CrewConsumables] = Field(DemandModelKind.CrewConsumables, description="the demand model's type")

    reserves_duration: float = Field(..., title="Reserves Duration")
    water_recovery_rate: float = Field(..., title="Water Recovery Rate")
    clothing_lifetime: float = Field(..., title="Clothing Lifetime")
    transit_demand_omitted: bool = Field(..., title="Transit Demand Omitted")
    water_rate: float = Field(default=3.6, title="Water Rate")
    eva_water_rate: float = Field(default=0.6875, title="EVA Water Rate")
    food_support_rate: float = Field(default=0.05556, title="Food Support Rate")
    ambient_food_rate: float = Field(default=0.76389, title="Ambient Food Rate")
    rf_food_rate: float = Field(default=1.61667, title="Rf Food Rate")
    oxygen_rate: float = Field(default=3.85714, title="Oxygen Rate")
    eva_oxygen_rate: float = Field(default=0.07875, title="EVA Oxygen Rate")
    nitrogen_rate: float = Field(default=2.21429, title="Nitrogen Rate")
    hygiene_rate: float = Field(default=0.27778, title="Hygiene Rate")
    hygiene_kit: float = Field(default=1.8, title="Hygiene Kit")
    clothing_rate: float = Field(default=2.3, title="Clothing Rate")
    personal_items: float = Field(default=10, title="Personal Items")
    office_equipment: float = Field(default=5, title="Office Equipment")
    eva_suit: float = Field(default=107, title="EVA Suit")
    eva_lithium_hydroxide: float = Field(default=0.3625, title="EVA Lithium Hydroxide")
    health_equipment: float = Field(default=20, title="Health Equipment")
    health_consumables: float = Field(default=0.1, title="Health Consumables")
    safety_equipment: float = Field(default=25, title="Safety Equipment")
    comm_equipment: float = Field(default=20, title="Comm Equipment")
    computer_equipment: float = Field(default=5, title="Computer Equipment")
    trash_bag_rate: float = Field(default=0.05, title="Trash Bag Rate")
    waste_containment_rate: float = Field(default=0.05, title="Waste Containment Rate")


class TimedImpulseDemandModel(ElementDemandModel, MissionDemandModel):
    """
    Demand model consuming a resource in one instant.

    :param bool processed: flag using in simulation to determine whether or not a demand has been processed.
    :param TimedImpulse type: demand model's type
    :param [Demand] demands: a list of demands of the given demand model
    """
    processed: bool = Field(default=False, title="flag")
    type: Literal[DemandModelKind.TimedImpulse] = Field(DemandModelKind.TimedImpulse, description="the demand model's type")
    demands: List[Union[ResourceAmount, GenericResourceAmount]] = Field(..., description="a list of the demands of the given demand model")


class RatedDemandModel(ElementDemandModel, MissionDemandModel):
    """
    Demand model consuming a resource in one instant.

    :param Rated type: demand model's type
    :param [Demand] demands: a list of the rated demands of the given demand model
    """
    type: Literal[DemandModelKind.Rated] = Field(DemandModelKind.Rated, description="the demand model's type")
    demands: List[Union[ResourceAmountRate, GenericResourceAmountRate]] = Field(..., description="a list of the rated demands of the given demand model")


class SparingByMassDemandModel(ElementDemandModel):
    """
    Demand model consuming a resource in one instant.

    :param SparingByMass type: demand model's type
    :param float unpressurizedSparesRate: percentage of an element's mass demanded as unpressurized spares each year
    :param float pressurizedSparesRate: percentage of an element's mass demanded as pressurized spares each year
    :param bool partsListEnabled: true if the element's part list should be used to drive demand resources

    """
    #TODO: review and compare with json
    type: Literal[DemandModelKind.SparingByMass] = Field(DemandModelKind.SparingByMass, description="the demand model's type")
    unpressurizedSparesRate: float = Field(..., title="Unpressurized Spares Rate")
    pressurizedSparesRate: float = Field(..., title="Pressurized Spares Rate")
    partsListEnabled: bool = Field(..., title="Parts List Enabled")




AllDemandModels = Union[
    TimedImpulseDemandModel,
    RatedDemandModel,
    CrewConsumablesDemandModel,
    SparingByMassDemandModel
]