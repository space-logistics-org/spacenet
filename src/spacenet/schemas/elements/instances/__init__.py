"""Defines object schemas for instantiated elements."""

from typing import Union

from .element import InstElementUUID, InstElement
from .container import InstResourceContainer
from .carrier import InstElementCarrier, InstSurfaceVehicle, InstPropulsiveVehicle
from .agent import InstHumanAgent, InstRoboticAgent

AllInstElements = Union[
    InstElement,
    InstResourceContainer,
    InstElementCarrier,
    InstPropulsiveVehicle,
    InstSurfaceVehicle,
    InstHumanAgent,
    InstRoboticAgent,
]
