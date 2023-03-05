"""Defines object schemas for demand model instances."""

from typing import Union

from .demand_models import (
    InstElementDemandModel,
    InstMissionDemandModel,
    InstCrewConsumablesDemandModel,
    InstTimedImpulseDemandModel,
    InstRatedDemandModel,
    InstSparingByMassDemandModel,
)


AllInstMissionDemandModels = Union[
    InstTimedImpulseDemandModel,
    InstRatedDemandModel,
    InstCrewConsumablesDemandModel,
]
AllInstElementDemandModels = Union[
    InstTimedImpulseDemandModel, InstRatedDemandModel, InstSparingByMassDemandModel
]
AllInstDemandModels = Union[
    InstTimedImpulseDemandModel,
    InstRatedDemandModel,
    InstCrewConsumablesDemandModel,
    InstSparingByMassDemandModel,
]
