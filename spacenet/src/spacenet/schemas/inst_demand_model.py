"""
This module defines schemas for specifying mission-wide demand models.
"""
from abc import ABC
from math import inf
from uuid import uuid4, UUID
from typing import Union, List, Optional
from enum import Enum

from pydantic import BaseModel, Field
from fastapi_camelcase import CamelModel
from typing_extensions import Literal

from .demand_model import DemandModelType
from .resource import ResourceAmount, ResourceAmountRate, GenericResourceAmount, GenericResourceAmountRate
from .mixins import ImmutableBaseModel


__all__ = [
    "InstTimedImpulseDemandModel",
    "InstRatedDemandModel",
    "InstSparingByMassDemandModel",
    "InstCrewConsumablesDemandModel",
    "AllInstMissionDemandModels",
    "AllInstElementDemandModels"
]

class InstDemandModelUUID(ImmutableBaseModel, ABC):
    """
    A base class for instantiated demand models defining only the UUID.

    :param UUID id: unique identifier for element

    """
    name: str = Field(..., title="Name")
    template_id: UUID = Field(..., description="UUID of the template for this instantiated demand model")

class InstElementDemandModel(InstDemandModelUUID, ABC):
    """
    Element Demand Model base class.

    :param str name: name of demand model
    """
    pass

class InstMissionDemandModel(InstDemandModelUUID, ABC):
    """
    Mission Demand Model base class.

    :param str name: name of demand model
    """
    pass

class InstCrewConsumablesDemandModel(InstMissionDemandModel):
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
    type: Literal[DemandModelType.CrewConsumables] = Field(DemandModelType.CrewConsumables, description="the demand model's type")

    reserves_duration: Optional[float] = Field(title="Reserves Duration")
    water_recovery_rate: Optional[float] = Field(title="Water Recovery Rate")
    clothing_lifetime: Optional[float] = Field(title="Clothing Lifetime")
    transit_demands_omitted: Optional[bool] = Field(title="Transit Demand Omitted")
    water_rate: Optional[float] = Field(title="Water Rate")
    eva_water_rate: Optional[float] = Field(title="EVA Water Rate")
    food_support_rate: Optional[float] = Field(title="Food Support Rate")
    ambient_food_rate: Optional[float] = Field(title="Ambient Food Rate")
    rf_food_rate: Optional[float] = Field(title="Rf Food Rate")
    oxygen_rate: Optional[float] = Field(title="Oxygen Rate")
    eva_oxygen_rate: Optional[float] = Field(title="EVA Oxygen Rate")
    nitrogen_rate: Optional[float] = Field(title="Nitrogen Rate")
    hygiene_rate: Optional[float] = Field(title="Hygiene Rate")
    hygiene_kit: Optional[float] = Field(title="Hygiene Kit")
    clothing_rate: Optional[float] = Field(title="Clothing Rate")
    personal_items: Optional[float] = Field(title="Personal Items")
    office_equipment: Optional[float] = Field(title="Office Equipment")
    eva_suit: Optional[float] = Field(title="EVA Suit")
    eva_lithium_hydroxide: Optional[float] = Field(title="EVA Lithium Hydroxide")
    health_equipment: Optional[float] = Field(title="Health Equipment")
    health_consumables: Optional[float] = Field(title="Health Consumables")
    safety_equipment: Optional[float] = Field(title="Safety Equipment")
    comm_equipment: Optional[float] = Field(title="Comm Equipment")
    computer_equipment: Optional[float] = Field(title="Computer Equipment")
    trash_bag_rate: Optional[float] = Field(title="Trash Bag Rate")
    waste_containment_rate: Optional[float] = Field(title="Waste Containment Rate")


class InstTimedImpulseDemandModel(InstElementDemandModel, InstMissionDemandModel):
    """
    Demand model consuming a resource in one instant.

    :param bool processed: flag using in simulation to determine whether or not a demand has been processed.
    :param TimedImpulse type: demand model's type
    :param [Demand] demands: a list of demands to occur at one instant in time
    """
    type: Literal[DemandModelType.TimedImpulse] = Field(DemandModelType.TimedImpulse, description="The demand model's type")
    processed: Optional[bool] = Field(title="flag")
    demands: Optional[List[Union[ResourceAmount, GenericResourceAmount]]] = Field(description="A list of the demands to occur at one instant in time")


class InstRatedDemandModel(InstElementDemandModel, InstMissionDemandModel):
    """
    Demand model consuming a resource in one instant.

    :param Rated type: demand model's type
    :param [Demand] demands: a list of resources and rates at which they are demanded
    """
    type: Literal[DemandModelType.Rated] = Field(DemandModelType.Rated, description="The demand model's type")
    demands: Optional[List[Union[ResourceAmountRate, GenericResourceAmountRate]]] = Field(description="A list of resources and rates at which they are demanded")


class InstSparingByMassDemandModel(InstElementDemandModel):
    """
    Demand model consuming a resource in one instant.

    :param SparingByMass type: demand model's type
    :param float unpressurizedSparesRate: percentage of an element's mass demanded as unpressurized spares each year
    :param float pressurizedSparesRate: percentage of an element's mass demanded as pressurized spares each year
    :param bool partsListEnabled: true if the element's part list should be used to drive demand resources

    """
    type: Literal[DemandModelType.SparingByMass] = Field(DemandModelType.SparingByMass, description="The demand model's type")
    unpressurized_spares_rate: Optional[float] = Field(title="Unpressurized Spares Rate", description="Percentage of an element's mass demanded as unpressurized spares each year")
    pressurized_spares_rate: Optional[float] = Field(title="Pressurized Spares Rate", description="Percentage of an element's mass demanded as pressurized spares each year")
    parts_list_enabled: Optional[bool] = Field(title="Parts List Enabled", description="True if the element's part list should be used to drive demand resources")

AllInstMissionDemandModels = Union[
    InstTimedImpulseDemandModel,
    InstRatedDemandModel,
    InstCrewConsumablesDemandModel,
]
AllInstElementDemandModels = Union[
    InstTimedImpulseDemandModel,
    InstRatedDemandModel,
    InstSparingByMassDemandModel
]
