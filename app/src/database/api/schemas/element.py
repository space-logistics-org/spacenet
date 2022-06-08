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
from spacenet.src.schemas.element import *
from spacenet.src.schemas.mixins import ReadSchema, RequiresOnlyType

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
    """
    Update variant of Element
    """
    pass


class ElementRead(Element, ReadSchema):
    """
    Read variant of Element
    """
    pass


class ElementCarrierUpdate(ElementCarrier, RequiresOnlyType):
    """
    Update variant of ElementCarrier
    """
    pass


class ElementCarrierRead(ElementCarrier, ReadSchema):
    """
    Read variant of ElementCarrier
    """
    pass


class ResourceContainerUpdate(ResourceContainer, RequiresOnlyType):
    """
    Update variant of ResourceContainer
    """
    pass


class ResourceContainerRead(ResourceContainer, ReadSchema):
    """
    Read variant of ResourceContainer
    """
    pass


class SurfaceVehicleUpdate(SurfaceVehicle, RequiresOnlyType):
    """
    Update variant of SurfaceVehicle
    """
    pass


class SurfaceVehicleRead(SurfaceVehicle, ReadSchema):
    """
    Read variant of SurfaceVehicle
    """
    pass


class PropulsiveVehicleUpdate(PropulsiveVehicle, RequiresOnlyType):
    """
    Update variant of PropulsiveVehicle
    """
    pass


class PropulsiveVehicleRead(PropulsiveVehicle, ReadSchema):
    """
    Read variant of PropulsiveVehicle
    """
    pass


class HumanAgentUpdate(HumanAgent, RequiresOnlyType):
    """
    Update variant of HumanAgent
    """
    pass


class HumanAgentRead(HumanAgent, ReadSchema):
    """
    Read variant of HumanAgent
    """
    pass


class RoboticAgentUpdate(RoboticAgent, RequiresOnlyType):
    """
    Update variant of RoboticAgent
    """
    pass


class RoboticAgentRead(RoboticAgent, ReadSchema):
    """
    Read variant of RoboticAgent
    """
    pass
