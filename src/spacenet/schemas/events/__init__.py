"""Events define the state transitions that drive simulation behavior."""

from typing import Union

from .create_elements import CreateElements
from .move_elements import MoveElements
from .remove_elements import RemoveElements
from .reconfigure_element import ReconfigureElement
from .reconfigure_elements import ReconfigureElements

from .add_resources import AddResources
from .consume_resources import ConsumeResources
from .transfer_resources import TransferResources
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
