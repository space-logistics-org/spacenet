"""
This module defines the database schema for element demand models and element demand model subclasses.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean

from ..database import Base
from spacenet.schemas.element_demand_model import DemandModelType
from spacenet.schemas.element import *

# from  spacenet.schemas.mission import *

__all__ = ["DemandModelType", "DemandModel", "CrewConsumablesDemandModel",
           "TimedImpulseDemandModel", "RatedDemandModel", "SparingByMassDemandModel"]


class DemandModel(Base):
    __tablename__ = "Demand Models"
    id = Column(Integer, primary_key=True)
    type = Column(String)

    __mapper_args__ = {"polymorphic_identity": "demandModel", "polymorphic_on": type}


class CrewConsumablesDemandModel(DemandModel):
    # mission = Column(Mission)
    reservesDuration = Column(Float)
    waterRecoveryRate = Column(Float)
    clothingLifetime = Column(Float)
    transitDemandOmitted = Column(Boolean)
    waterRate = Column(Float)
    evaWaterRate = Column(Float)
    foodSupportRate = Column(Float)
    ambientFoodRate = Column(Float)
    rfFoodRate = Column(Float)
    oxygenRate = Column(Float)
    evaOxygenRate = Column(Float)
    nitrogenRate = Column(Float)
    hygieneRate = Column(Float)
    hygieneKit = Column(Float)
    clothingRate = Column(Float)
    personalItems = Column(Float)
    officeEquipment = Column(Float)
    evaSuit = Column(Float)
    evaLithiumHydroxide = Column(Float)
    healthEquipment = Column(Float)
    healthConsumables = Column(Float)
    safetyEquipment = Column(Float)
    commEquipment = Column(Float)
    computerEquipment = Column(Float)
    trashBagRate = Column(Float)
    wasteContainmentRate = Column(Float)

    __mapper_args__ = {"polymorphic_identity": DemandModelType.crew_consumables}


class TimedImpulseDemandModel(DemandModel):
    # demands = Column(DemandSet)
    flag = Column(Boolean)

    __mapper_args__ = {"polymorphic_identity": DemandModelType.timed_impulse}


class RatedDemandModel(DemandModel):
    # demands = Column(DemandSet)

    __mapper_args__ = {"polymorphic_identity": DemandModelType.rated}


class SparingByMassDemandModel(DemandModel):
    # element = Column(I_Element)
    unpressurizedSparesRates = Column(Float)
    pressurizedSparesRates = Column(Float)
    partsListEnabled = Column(Boolean)

    __mapper_args__ = {"polymorphic_identity": DemandModelType.sparing_by_mass}
