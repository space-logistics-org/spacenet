from enum import Enum

from pydantic import BaseModel, Field


# import spacenet.domain.resource.Demand
# import spacenet.domain.resource.DemandSet
# from spacenet.schemas.Mission import *
# import spacenet.simulator.I_Simulator

class DemandModelType(str, Enum):
    crew_consumables = "Crew Consumables Demand Model"
    timed_impulse = "Timed Impulse Demand Model"
    rated = "Rated Demand Model"
    sparing_by_mass = "Sparing by Mass Demand Model"
    class Config:
        title: "Demand Model Type"

class DemandModel(BaseModel):
    name: str = Field(..., title="Name")


class CrewConsumablesDemandModel(DemandModel):
    type: DemandModelType = Field(default=DemandModelType.crew_consumables, title="Type", description="Demand model type")

    # mission: Mission = Field(..., title="Mission")

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
    # demands: DemandSet = Field(..., title="Demands")
    flag: bool = Field(default=False, title="flag")


class RatedDemandModel(DemandModel):
    # demandRates: DemandSet = Field(..., title="Demand Rates")
    pass

class SparingByMassDemandModel(DemandModel):
    # element: I_Element = Field(..., title="Element")
    unpressurizedSparesRates: float = Field(..., title="Unpressurized Spares Rates")
    pressurizedSparesRates: float = Field(..., title="Pressurized Spares Rates")
    partsListEnabled: bool = Field(..., title="Parts List Enabled")
