"""
This module defines schemas for specifying the operational state of elements.
"""
from typing import List, Optional, Union
from enum import Enum
from uuid import uuid4, UUID

from pydantic import BaseModel, Field, StrictBool, conint

from .mixins import ImmutableBaseModel
from .constants import SQLITE_MAX_INT, SQLITE_MIN_INT
from .inst_element_demand_model import AllInstElementDemandModels
from .state import StateType

__all__ = ["InstState", "InstStateUUID"]

class InstStateUUID(ImmutableBaseModel):
    """
    A representation of a state using only its UUID. This serves as a base class for all states.
    """
    id: UUID = Field(default_factory=uuid4, description="unique identifier for state")


class InstState(InstStateUUID):
    """
    An abbreviated representation of the state of a specific element.
    """
    template_id: UUID = Field(..., description="UUID of the state upon which the instantiated state is based")
    name: Optional[str] = Field(description="the name of this state")
    description: Optional[str] = Field(
        title="Description", description="short description of the state"
    )
    state_type: Optional[StateType] = Field(
        description="the general classification of this state"
    )
    is_initial_state: Optional[StrictBool] = Field(
        description="a boolean flag representing if this state is the state an element starts in or not",
    )
    demand_models: Optional[List[AllInstElementDemandModels]]
