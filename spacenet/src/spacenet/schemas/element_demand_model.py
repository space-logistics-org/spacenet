"""
This module defines a schema for specifying how various element types require continual
resources.
"""
from typing import List, Optional, Union
from enum import Enum
from uuid import uuid4, UUID

from pydantic import BaseModel, Field
from typing_extensions import Literal
from .mixins import ImmutableBaseModel

from .demand import DemandModelKind, Demand, DemandRate
from .resource import ResourceUUID, ResourceType

__all__ = [
    "DemandModelUUID",
    "DemandModel",
    "CrewConsumablesDemandModel",
    "TimedImpulseDemandModel",
    "RatedDemandModel",
    "SparingByMassDemandModel",
]


class DemandModelUUID(ImmutableBaseModel):
    """
    A representation of a demand model containing only its UUID and serving as a base class for all other demand models.

    :param UUID id: unique identifier for element demand model
    """
    id: UUID = Field(default_factory=uuid4, description="unique identifier for demand model")

class DemandModel(DemandModelUUID):
    """
    Element Demand Model base class.

    :param str name: name of demand model
    """
    name: str = Field(..., title="Name")


class CrewConsumablesDemandModel(DemandModel):
    """
    Demands for consumables by crew.

    :param CrewConsumables type: 
    :param float reservesDuration: 
    :param float waterRecoveryRate: 
    :param float clothingLifetime: 
    :param float transitDemandOmitted: 
    :param float waterRate: 
    :param float evaWaterRate: 
    :param float foodSupportRate: 
    :param float ambientFoodRate: 
    :param float rfFoodRate: 
    :param float oxygenRate: 
    :param float evaOxygenRate: 
    :param float nitrogenRate: 
    :param float hygieneRate: 
    :param float hygieneKit: 
    :param float clothingRate: 
    :param float personalItems: 
    :param float officeEquipment: 
    :param float evaSuit: 
    :param float evaLithiumHydroxide: 
    :param float healthEquipment: 
    :param float healthConsumables: 
    :param float safetyEquipment: 
    :param float commEquipment: 
    :param float computerEquipment: 
    :param float trashBagRate: 
    :param float wasteContainmentRate: 
    """
    type: Literal[DemandModelKind.CrewConsumables] = Field(DemandModelKind.CrewConsumables, description="the demand model's type")

    reservesDuration: float = Field(..., title="Reserves Duration")
    waterRecoveryRate: float = Field(..., title="Water Recovery Rate")
    clothingLifetime: float = Field(..., title="Clothing Lifetime")
    transitDemandOmitted: bool = Field(..., title="Transit Demand Omitted")
    waterRate: float = Field(default=3.6, title="Water Rate")
    evaWaterRate: float = Field(default=0.6875, title="EVA Water Rate")
    foodSupportRate: float = Field(default=0.05556, title="Food Support Rate")
    ambientFoodRate: float = Field(default=0.76389, title="Ambient Food Rate")
    rfFoodRate: float = Field(default=1.61667, title="Rf Food Rate")
    oxygenRate: float = Field(default=3.85714, title="Oxygen Rate")
    evaOxygenRate: float = Field(default=0.07875, title="EVA Oxygen Rate")
    nitrogenRate: float = Field(default=2.21429, title="Nitrogen Rate")
    hygieneRate: float = Field(default=0.27778, title="Hygiene Rate")
    hygieneKit: float = Field(default=1.8, title="Hygiene Kit")
    clothingRate: float = Field(default=2.3, title="Clothing Rate")
    personalItems: float = Field(default=10, title="Personal Items")
    officeEquipment: float = Field(default=5, title="Office Equipment")
    evaSuit: float = Field(default=107, title="EVA Suit")
    evaLithiumHydroxide: float = Field(default=0.3625, title="EVA Lithium Hydroxide")
    healthEquipment: float = Field(default=20, title="Health Equipment")
    healthConsumables: float = Field(default=0.1, title="Health Consumables")
    safetyEquipment: float = Field(default=25, title="Safety Equipment")
    commEquipment: float = Field(default=20, title="Comm Equipment")
    computerEquipment: float = Field(default=5, title="Computer Equipment")
    trashBagRate: float = Field(default=0.05, title="Trash Bag Rate")
    wasteContainmentRate: float = Field(default=0.05, title="Waste Containment Rate")


class TimedImpulseDemandModel(DemandModel):
    """
    Demand model consuming a resource in one instant.

    :param bool processed: flag using in simulation to determine whether or not a demand has been processed.
    :param TimedImpulse type: demand model's type
    :param [Demand] demands: a list of demands of the given demand model
    """
    processed: bool = Field(default=False, title="flag")
    type: Literal[DemandModelKind.TimedImpulse] = Field(DemandModelKind.TimedImpulse, description="the demand model's type")
    demands: List[Demand] = Field(..., description="a list of the demands of the given demand model")


class RatedDemandModel(DemandModel):
    """
    Demand model consuming a resource in one instant.

    :param Rated type: demand model's type
    :param [Demand] demands: a list of the rated demands of the given demand model
    """
    type: Literal[DemandModelKind.Rated] = Field(DemandModelKind.Rated, description="the demand model's type")
    demands: List[DemandRate] = Field(..., description="a list of the rated demands of the given demand model")


class SparingByMassDemandModel(DemandModel):
    """
    Demand model consuming a resource in one instant.

    :param SparingByMass type: demand model's type
    :param [Demand] demands: a list of the rated demands of the given demand model
    :param float unpressurizedSparesRate
    :param float pressurizedSparesRate
    :param float partsListEnabled

    """
    type: Literal[DemandModelKind.SparingByMass] = Field(DemandModelKind.SparingByMass, description="the demand model's type")
    unpressurizedSparesRate: float = Field(..., title="Unpressurized Spares Rate")
    pressurizedSparesRate: float = Field(..., title="Pressurized Spares Rate")
    partsListEnabled: bool = Field(..., title="Parts List Enabled")


AllElementDemandModels = Union[
    DemandModel,
    CrewConsumablesDemandModel,
    TimedImpulseDemandModel,
    RatedDemandModel,
    SparingByMassDemandModel
]