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
    """
    resourceType: ResourceType = Field(
        ...,
        title="Resource Type",
        description="Type of resource that is being demanded.",
    )
    resource: ResourceUUID = Field(..., title="Resource ID", description="UUID of resource being consumed")
    amount: float = Field(..., title="Amount", description="amount of the resource being consumed, in units defined by given resource")

class DemandRate(BaseModel):
    """
    A representation of one specific demand, particularly including the type, UUID and amount of resource demanded.
    """
    resourceType: ResourceType = Field(
        ...,
        title="Resource Type",
        description="Type of resource that is being demanded.",
    )
    resource: ResourceUUID = Field(..., title="Resource ID", description="UUID of resource being consumed")
    rate: float = Field(..., title="Amount", description="rate of resource consumption, in units defined by given resource")
