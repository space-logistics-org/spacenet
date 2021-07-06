"""
This module defines the schemas for Read and Update variants of elements and the corresponding
subtypes. The variants for update operations make all fields optional except for a type
discriminant, and the variant for read operations requires returning a unique identifier
alongside all other data.

Internally, multiple mixins are used to generate the aforementioned behaviors: a mixin
implements requiring an ID, and another implements making a subset of fields optional. This
means that fields are specified in as few places as possible.

The module exports the schemas for Elements and corresponding subtypes explicitly.
"""
from spacenet.schemas.element import (
    Element,
    ElementCarrier,
    HumanAgent,
    PropulsiveVehicle,
    ResourceContainer,
    RoboticAgent,
    SurfaceVehicle,
)
from spacenet.schemas.mixins import ReadSchema, RequiresOnlyType

__all__ = [
    "Element",
    "ElementUpdate",
    "ElementRead",
    "ElementCarrier",
    "ElementCarrierUpdate",
    "ElementCarrierRead",
    "ResourceContainer",
    "ResourceContainerUpdate",
    "ResourceContainerRead",
    "SurfaceVehicle",
    "SurfaceVehicleUpdate",
    "SurfaceVehicleRead",
    "PropulsiveVehicle",
    "PropulsiveVehicleUpdate",
    "PropulsiveVehicleRead",
    "HumanAgent",
    "HumanAgentRead",
    "HumanAgentUpdate",
    "RoboticAgent",
    "RoboticAgentRead",
    "RoboticAgentUpdate",
]


class ElementUpdate(Element, RequiresOnlyType):
    pass


class ElementRead(Element, ReadSchema):
    pass


class ElementCarrierUpdate(ElementCarrier, RequiresOnlyType):
    pass


class ElementCarrierRead(ElementCarrier, ReadSchema):
    pass


class ResourceContainerUpdate(ResourceContainer, RequiresOnlyType):
    pass


class ResourceContainerRead(ResourceContainer, ReadSchema):
    pass


class SurfaceVehicleUpdate(SurfaceVehicle, RequiresOnlyType):
    pass


class SurfaceVehicleRead(SurfaceVehicle, ReadSchema):
    pass


class PropulsiveVehicleUpdate(PropulsiveVehicle, RequiresOnlyType):
    pass


class PropulsiveVehicleRead(PropulsiveVehicle, ReadSchema):
    pass


class HumanAgentUpdate(HumanAgent, RequiresOnlyType):
    pass


class HumanAgentRead(HumanAgent, ReadSchema):
    pass


class RoboticAgentUpdate(RoboticAgent, RequiresOnlyType):
    pass


class RoboticAgentRead(RoboticAgent, ReadSchema):
    pass
