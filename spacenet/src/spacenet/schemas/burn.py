"""
This module defines a schema for specifying how various element types require continual
resources.
"""
from typing import List, Optional, Union
from enum import Enum
from uuid import uuid4, UUID
from datetime import timedelta

from pydantic import BaseModel, Field
from typing_extensions import Literal

from .resource import ResourceUUID, ResourceType
from .types import SafeNonNegFloat

__all__ = [
    "Burn"
]

class Burn(BaseModel):
    """
    An individual burn to generate a specified amount of
    velocity change. Base class for propulsive burns
    
    """

    id: UUID = Field(..., title="UUID", description="UUID of individual burn")
    time: timedelta = Field(
        ..., description="Mission time at which the burn will occur"
    )
    delta_v: SafeNonNegFloat = Field(
        ..., description="Change in velocity to be achieved by a burn"
    )