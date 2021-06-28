from enum import Enum

from pydantic import BaseModel, StrictBool

__all__ = [
    "State",
    "StateType"
]


class StateType(str, Enum):
    Active = "Active"
    Quiescent = "Quiescent"
    Dormant = "Dormant"
    Decommissioned = "Decommissioned"


class State(BaseModel):
    element_id: int
    name: str
    state_type: StateType
    is_initial_state: StrictBool
