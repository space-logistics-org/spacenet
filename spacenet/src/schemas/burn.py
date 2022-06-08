"""
This module defines a schema for specifying how various element types require continual
resources.
"""
from uuid import uuid4, UUID
from datetime import timedelta

from pydantic import BaseModel, Field

from .mixins import ImmutableBaseModel
from .types import SafeNonNegFloat

__all__ = [
    "BurnUUID",
    "Burn"
]

class BurnUUID(ImmutableBaseModel):
    """
    A base class for burns defined only by UUID.

    :param UUID id: unique identifier for burn
    """
    id: UUID = Field(default_factory=uuid4, description="unique identifier for burn")

class Burn(BaseModel):
    """
    An individual burn to generate a specified amount of
    velocity change. Base class for propulsive burns
    
    :param UUID id: unique identifier for individual burn
    :param timedelta time: amount of time the burn will take
    :param SafeNonNegFloat delta_v: change in velocity to be achieved by a burnS
    """

    id: UUID = Field(..., title="UUID", description="UUID of individual burn")
    time: timedelta = Field(
        ..., description="amount of time the burn will take"
    )
    delta_v: SafeNonNegFloat = Field(
        ..., description="Change in velocity to be achieved by a burn"
    )