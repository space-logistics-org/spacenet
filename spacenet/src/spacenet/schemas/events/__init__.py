"""Defines object schemas for events."""

from typing import Union

from .elements import (
    CreateElements,
    MoveElements,
    RemoveElements,
    ReconfigureElement,
    ReconfigureElements,
)
from .resources import AddResources, ConsumeResources, TransferResources
from .burn import PropulsiveBurn, BurnStageItem
from .exploration import CrewedEVA, CrewedExploration, ElementState
from .transport import (
    SurfaceTransport,
    FlightTransport,
    SpaceTransport,
    BurnStageSequence,
)

AllEvents = Union[
    CreateElements,
    MoveElements,
    RemoveElements,
    ReconfigureElement,
    ReconfigureElements,
    AddResources,
    ConsumeResources,
    TransferResources,
    PropulsiveBurn,
    CrewedEVA,
    CrewedExploration,
    SurfaceTransport,
    FlightTransport,
    SpaceTransport,
]
