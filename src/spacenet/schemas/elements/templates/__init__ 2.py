"""Defines object schemas for element templates."""

from typing import Union

from .agent import HumanAgent, RoboticAgent
from .carrier import ElementCarrier, PropulsiveVehicle, SurfaceVehicle
from .container import ResourceContainer
from .element import Element, ElementType, ElementUUID

AllElements = Union[
    Element,
    ResourceContainer,
    ElementCarrier,
    SurfaceVehicle,
    PropulsiveVehicle,
    HumanAgent,
    RoboticAgent,
]
