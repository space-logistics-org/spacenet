"""
This module defines a schema for specifying how various element types require continual
resources.
"""
from typing import List, Optional, Union
from enum import Enum
from uuid import uuid4, UUID

from pydantic import BaseModel, Field
from typing_extensions import Literal
from .mixins import ImmutableBaseModel

from .resource import ResourceUUID, ResourceType
from .constants import ClassOfSupply

__all__ = [
    "DemandModelKind",
    "Demand",
    "DemandRate"
]


class DemandModelKind(str, Enum):
    """
    An enumeration of all the types of Demand Model.
    """
    CrewConsumables = "CrewConsumables"
    TimedImpulse = "TimedImpulse"
    Rated = "Rated"
    SparingByMass = "SparingByMass"

class Demand(BaseModel):
    """
    A representation of one specific demand, particularly including the type, UUID and amount of resource demanded.
    
    :param ResourceType resource_type: type of resource that is being demanded (continuous or discrete)
    :param ResourceUUID | ClassofSupply resource: UUID of COS number of the resource demanded
    :param float amount: amount of the resource being demanded, in units defined by given resource
    """
    resource_type: ResourceType = Field(
        ...,
        title="Resource Type",
        description="Type of resource that is being demanded.",
    )
    resource: Union[ResourceUUID, ClassOfSupply] = Field(..., title="Resource", description="UUID or COS number of resource being demanded")
    amount: float = Field(..., title="Amount", description="amount of the resource being demanded, in units defined by given resource")

class DemandRate(BaseModel):
    """
    A representation of one specific demand, particularly including the type, UUID and amount of resource demanded.

    :param ResourceType resource_type: type of resource that is being demanded (continuous or discrete)
    :param ResourceUUID | ClassofSupply resource: UUID of COS number of the resource demanded
    :param float amount: rate of resource demand, in units defined by given resource
    """
    resource_type: ResourceType = Field(
        ...,
        title="Resource Type",
        description="Type of resource that is being demanded.",
    )
    resource: Union[ResourceUUID, ClassOfSupply] = Field(..., title="Resource", description="UUID or COS number of resource being demanded")
    rate: float = Field(..., title="Amount", description="rate of resource consumption, in units defined by given resource")
