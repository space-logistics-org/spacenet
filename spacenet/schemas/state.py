from enum import Enum

from pydantic import BaseModel, Field, StrictBool, conint

__all__ = ["State", "StateType"]

from .constants import SQLITE_MAX_INT, SQLITE_MIN_INT


class StateType(str, Enum):
    """
    An enumeration of the possible types/classifications of State.
    """

    Active = "Active"
    Quiescent = "Quiescent"
    Dormant = "Dormant"
    Decommissioned = "Decommissioned"


class State(BaseModel):
    """
    An abbreviated representation of the state of a specific element.
    """

    element_id: conint(ge=SQLITE_MIN_INT, le=SQLITE_MAX_INT, strict=True) = Field(
        ..., description="the id of the element this state refers to"
    )
    name: str = Field(..., description="the name of this state")
    state_type: StateType = Field(
        ..., description="the general classification of this state"
    )
    is_initial_state: StrictBool = Field(
        ...,
        description="a boolean flag representing if this state is the state an element starts in or not",
    )
