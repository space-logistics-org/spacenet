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

from .resource import ResourceUUID, ResourceType
from .element_demand_model import DemandModelKind

__all__ = [
    "InstDemandModelUUID",
    "InstDemandModel",
    "InstCrewConsumablesDemandModel",
    "InstTimedImpulseDemandModel",
    "InstRatedDemandModel",
    "InstSparingByMassDemandModel",
]

class InstElementDemand(BaseModel):
    """
    A representation of one specific demand, particularly including the type, UUID and amount of resource demanded.
    """
    resourceType: Optional[ResourceType] = Field(
        title="Resource Type",
        description="Type of resource that is being demanded.",
    )
    resource: Optional[ResourceUUID] = Field(title="Resource ID", description="UUID of resource being consumed")
    amount: Optional[float] = Field(title="Amount", description="amount of the resource being consumed, in units defined by given resource")

class InstDemandModelUUID(ImmutableBaseModel):
    """
    A representation of a demand model containing only its UUID and serving as a base class for all other demand models.
    """
    id: UUID = Field(default_factory=uuid4, description="unique identifier for demand model")

class InstDemandModel(InstDemandModelUUID):
    """
    Element Demand Model base class.
    """
    template_id: UUID = Field(..., description="UUID of demand model upon which instance is based")
    name: Optional[str] = Field(title="Name")


class InstCrewConsumablesDemandModel(InstDemandModel):
    type: Literal[DemandModelKind.CrewConsumables] = Field(description="the demand model's type")

    reservesDuration: Optional[float] = Field(title="Reserves Duration")
    waterRecoveryRate: Optional[float] = Field(title="Water Recovery Rate")
    clothingLifetime: Optional[float] = Field(title="Clothing Lifetime")
    transitDemandOmitted: bool = Field(title="Transit Demand Omitted")
    waterRate: Optional[float] = Field(default=3.6, title="Water Rate")
    evaWaterRate: Optional[float] = Field(default=0.6875, title="EVA Water Rate")
    foodSupportRate: Optional[float] = Field(default=0.05556, title="Food Support Rate")
    ambientFoodRate: Optional[float] = Field(default=0.76389, title="Ambient Food Rate")
    rfFoodRate: Optional[float] = Field(default=1.61667, title="Rf Food Rate")
    oxygenRate: Optional[float] = Field(default=3.85714, title="Oxygen Rate")
    evaOxygenRate: Optional[float] = Field(default=0.07875, title="EVA Oxygen Rate")
    nitrogenRate: Optional[float] = Field(default=2.21429, title="Nitrogen Rate")
    hygieneRate: Optional[float] = Field(default=0.27778, title="Hygiene Rate")
    hygieneKit: Optional[float] = Field(default=1.8, title="Hygiene Kit")
    clothingRate: Optional[float] = Field(default=2.3, title="Clothing Rate")
    personalItems: Optional[float] = Field(default=10, title="Personal Items")
    officeEquipment: Optional[float] = Field(default=5, title="Office Equipment")
    evaSuit: Optional[float] = Field(default=107, title="EVA Suit")
    evaLithiumHydroxide: Optional[float] = Field(default=0.3625, title="EVA Lithium Hydroxide")
    healthEquipment: Optional[float] = Field(default=20, title="Health Equipment")
    healthConsumables: Optional[float] = Field(default=0.1, title="Health Consumables")
    safetyEquipment: Optional[float] = Field(default=25, title="Safety Equipment")
    commEquipment: Optional[float] = Field(default=20, title="Comm Equipment")
    computerEquipment: Optional[float] = Field(default=5, title="Computer Equipment")
    trashBagRate: Optional[float] = Field(default=0.05, title="Trash Bag Rate")
    wasteContainmentRate: Optional[float] = Field(default=0.05, title="Waste Containment Rate")


class InstTimedImpulseDemandModel(InstDemandModel):
    flag: Optional[bool] = Field(default=False, title="flag")
    type: Optional[Literal[DemandModelKind.TimedImpulse]] = Field(description="the demand model's type")


class InstRatedDemandModel(InstDemandModel):
    type: Optional[Literal[DemandModelKind.Rated]] = Field(description="the demand model's type")
    demands: Optional[List[InstElementDemand]] = Field(description="a list of the demands of the given demand model")


class InstSparingByMassDemandModel(InstDemandModel):
    type: Optional[Literal[DemandModelKind.SparingByMass]] = Field(description="the demand model's type")
    unpressurizedSparesRates: Optional[float] = Field(title="Unpressurized Spares Rates")
    pressurizedSparesRates: Optional[float] = Field(title="Pressurized Spares Rates")
    partsListEnabled: Optional[bool] = Field(title="Parts List Enabled")


AllInstElementDemandModels = Union[
    InstDemandModel,
    InstCrewConsumablesDemandModel,
    InstTimedImpulseDemandModel,
    InstRatedDemandModel,
    InstSparingByMassDemandModel
]