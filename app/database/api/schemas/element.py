"""
This module defines the schemas for Read and Update variants of elements and the corresponding
subtypes. The variants for update operations make all fields optional except for a type
discriminant, and the variant for read operations requires returning a unique identifier
alongside all other data.

Internally, multiple mixins are used to generate the aforementioned behaviors: a mixin
implements requiring a UUID, and another implements making a subset of fields optional. This
means that fields are specified in as few places as possible.

The module exports the schemas for Elements and corresponding subtypes explicitly.
"""
from spacenet.schemas.element import (
    Element,
    ElementCarrier,
    ResourceContainer,
    SurfaceVehicle,
    PropulsiveVehicle,
    HumanAgent,
    RoboticAgent,
)
from spacenet.schemas.mixins import RequiresUUID, RequiresOnlyType

__all__ = [
    "Element",
    "UpdateElement",
    "ReadElement",
    "ElementCarrier",
    "UpdateElementCarrier",
    "ReadElementCarrier",
    "ResourceContainer",
    "UpdateResourceContainer",
    "ReadResourceContainer",
    "SurfaceVehicle",
    "UpdateSurfaceVehicle",
    "ReadSurfaceVehicle",
    "PropulsiveVehicle",
    "UpdatePropulsiveVehicle",
    "ReadPropulsiveVehicle",
    "HumanAgent",
    "ReadHumanAgent",
    "UpdateHumanAgent",
    "RoboticAgent",
    "ReadRoboticAgent",
    "UpdateRoboticAgent",
]


class UpdateElement(Element, RequiresOnlyType):
    pass


class ReadElement(Element, RequiresUUID):
    pass


class UpdateElementCarrier(ElementCarrier, RequiresOnlyType):
    pass


class ReadElementCarrier(ElementCarrier, RequiresUUID):
    pass


class UpdateResourceContainer(ResourceContainer, RequiresOnlyType):
    pass


class ReadResourceContainer(ResourceContainer, RequiresUUID):
    pass


class UpdateSurfaceVehicle(SurfaceVehicle, RequiresOnlyType):
    pass


class ReadSurfaceVehicle(SurfaceVehicle, RequiresUUID):
    pass


class UpdatePropulsiveVehicle(PropulsiveVehicle, RequiresOnlyType):
    pass


class ReadPropulsiveVehicle(PropulsiveVehicle, RequiresUUID):
    pass


class UpdateHumanAgent(HumanAgent, RequiresOnlyType):
    pass


class ReadHumanAgent(HumanAgent, RequiresUUID):
    pass


class UpdateRoboticAgent(RoboticAgent, RequiresOnlyType):
    pass


class ReadRoboticAgent(RoboticAgent, RequiresUUID):
    pass
