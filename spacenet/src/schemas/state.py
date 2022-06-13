"""
This module defines schemas for specifying the operational state of elements.
"""
from typing import List, Optional, Union
from enum import Enum
from uuid import uuid4, UUID

from pydantic import BaseModel, Field, StrictBool, conint

from .mixins import ImmutableBaseModel
from .constants import SQLITE_MAX_INT, SQLITE_MIN_INT
from .demand_model import ElementDemandModelUUID

__all__ = ["State", "StateType", "StateUUID"]

class StateType(str, Enum):
    """
    An enumeration of the possible types/classifications of State.
    """

    Active = "Active"
    Quiescent = "Quiescent"
    Dormant = "Dormant"
    Decommissioned = "Decommissioned"

class StateUUID(ImmutableBaseModel):
    """
    A representation of a state using only its UUID. This serves as a base class for all states.
    """
    id: UUID = Field(default_factory=uuid4, description="unique identifier for state")


class State(StateUUID):
    """
    An abbreviated representation of the state of a specific element.
    """
    name: str = Field(..., description="the name of this state")
    description: str = Field(
        ..., title="Description", description="short description of the state"
    )
    type: StateType = Field(
        ..., description="the general classification of this state"
    )
    demand_models: List[ElementDemandModelUUID]
