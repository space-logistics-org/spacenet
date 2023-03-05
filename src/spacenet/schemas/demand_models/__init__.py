"""Defines object schemas for demand models."""

from .demand_model import DemandModelType
from .instances import (
    AllInstDemandModels,
    AllInstElementDemandModels,
    AllInstMissionDemandModels,
    InstCrewConsumablesDemandModel,
    InstElementDemandModel,
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
    MissionDemandModelUUID,
    RatedDemandModel,
    SparingByMassDemandModel,
    TimedImpulseDemandModel,
)
