"""Defines object schemas for elements."""

from typing import Union

from .element import ElementType, ElementUUID, Element
from .container import ResourceContainer
from .carrier import ElementCarrier, SurfaceVehicle, PropulsiveVehicle
from .agent import HumanAgent, RoboticAgent

from .inst_element import InstElementUUID, InstElement
from .inst_container import InstResourceContainer
from .inst_carrier import InstElementCarrier, InstSurfaceVehicle, InstPropulsiveVehicle
from .inst_agent import InstHumanAgent, InstRoboticAgent

from .state import StateType, State
from .part import Part

AllElements = Union[
    Element,
    ResourceContainer,
    ElementCarrier,
    SurfaceVehicle,
    PropulsiveVehicle,
    HumanAgent,
    RoboticAgent,
]

AllInstElements = Union[
    InstElement,
    InstResourceContainer,
    InstElementCarrier,
    InstPropulsiveVehicle,
    InstSurfaceVehicle,
    InstHumanAgent,
    InstRoboticAgent,
]
