"""
This module defines schemas for specifying the operational state of elements.
"""
from typing import List, Optional, Union
from enum import Enum
from uuid import uuid4, UUID
from fastapi_camelcase import CamelModel


from pydantic import BaseModel, Field, StrictBool, conint

from .types import SafeInt
from .mixins import ImmutableBaseModel
from .constants import SQLITE_MAX_INT, SQLITE_MIN_INT
from .inst_demand_model import InstElementDemandModel

__all__ = ["State", "StateType", "StateUUID", "ElementState"]

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

    :param UUID id: unique identifier for state
    """
    id: UUID = Field(default_factory=uuid4, description="unique identifier for state")


class State(StateUUID):
    """
    An abbreviated representation of the state of a specific element.

    :param str name: the name of this state
    :param str description: short description of the state
    :param StateType type: the general classificaton of this state
    :param [InstDemandModel] demand_models: list of instantiated demand models associated with this state
    """
    name: str = Field(..., description="the name of this state")
    description: str = Field(
        "", title="Description", description="short description of the state"
    )
    type: StateType = Field(
        ..., description="the general classification of this state"
    )
    demand_models: List[InstElementDemandModel] = Field(..., title="Demand Models", description="list of instantiated demand models associated with this state")

class ElementState(CamelModel):
    '''
    A utility class for specifying an element's new state.

    :param UUID element: UUID of the instantiated element whose state is to be changed
    :param SafeInt state_index: Index of the state to which this element should be reconfigured
    '''
    element: UUID = Field(..., title="element", description="UUID of the instantiated element whose state is to be changed")
    state_index: SafeInt = Field(..., title="State Index", description="Index of the state to which this element should be reconfigured")
