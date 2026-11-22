"""Defines object schemas for demand models."""

from .demand_model import DemandModelType
from .instances import (
    AllInstDemandModels,
    AllInstElementDemandModels,
    AllInstMissionDemandModels,
    InstCrewConsumablesDemandModel,
    InstElementDemandModel,
    InstISRUProcessDemandModel,
    InstMissionDemandModel,
    InstRatedDemandModel,
    InstSparingByMassDemandModel,
    InstTimedImpulseDemandModel,
)
from .templates import (
    AllDemandModels,
    AllElementDemandModels,
    AllMissionDemandModels,
    CrewConsumablesDemandModel,
    ElementDemandModelUUID,
    ISRUProcessDemandModel,
    MissionDemandModelUUID,
    RatedDemandModel,
    SparingByMassDemandModel,
    TimedImpulseDemandModel,
)
