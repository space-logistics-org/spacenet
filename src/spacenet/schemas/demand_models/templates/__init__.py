"""Defines object schemas for demand model templates."""

from typing import Union

from .demand_models import (
    ElementDemandModelUUID,
    MissionDemandModelUUID,
    CrewConsumablesDemandModel,
    TimedImpulseDemandModel,
    RatedDemandModel,
    SparingByMassDemandModel,
    ISRUProcessDemandModel,
)

AllMissionDemandModels = Union[
    TimedImpulseDemandModel,
    RatedDemandModel,
    CrewConsumablesDemandModel,
]
AllElementDemandModels = Union[
    TimedImpulseDemandModel,
    RatedDemandModel,
    SparingByMassDemandModel,
    ISRUProcessDemandModel,
]
AllDemandModels = Union[
    TimedImpulseDemandModel,
    RatedDemandModel,
    CrewConsumablesDemandModel,
    SparingByMassDemandModel,
    ISRUProcessDemandModel,
]
