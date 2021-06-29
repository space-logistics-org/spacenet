from enum import Enum

from pydantic import BaseModel, StrictBool, conint

__all__ = [
    "State",
    "StateType"
]

from spacenet.constants import SQLITE_MAX_INT, SQLITE_MIN_INT


class StateType(str, Enum):
    Active = "Active"
    Quiescent = "Quiescent"
    Dormant = "Dormant"
    Decommissioned = "Decommissioned"


class State(BaseModel):
    element_id: conint(ge=SQLITE_MIN_INT, le=SQLITE_MAX_INT, strict=True)
    name: str
    state_type: StateType
    is_initial_state: StrictBool
