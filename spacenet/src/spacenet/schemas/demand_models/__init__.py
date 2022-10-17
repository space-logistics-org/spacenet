"""Defines object schemas for demand models."""

from .demand_model import (
    ElementDemandModelUUID,
    MissionDemandModelUUID,
    CrewConsumablesDemandModel,
    TimedImpulseDemandModel,
    RatedDemandModel,
    SparingByMassDemandModel,
    AllMissionDemandModels,
    AllElementDemandModels,
    AllDemandModels,
)
from .inst_demand_model import (
    InstElementDemandModel,
    InstMissionDemandModel,
    InstCrewConsumablesDemandModel,
    InstTimedImpulseDemandModel,
    InstRatedDemandModel,
    InstSparingByMassDemandModel,
    AllInstMissionDemandModels,
    AllInstElementDemandModels,
    AllInstDemandModels,
)
