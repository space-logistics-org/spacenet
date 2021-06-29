from typing import Optional

from pydantic import StrictBool

from spacenet.schemas import ReadSchema, State, StateType


__all__ = [
    "State",
    "StateUpdate",
    "StateRead"
]


class StateUpdate(State):
    element_id: int
    name: Optional[str]
    state_type: Optional[StateType]
    is_initial_state: Optional[StrictBool]


class StateRead(State, ReadSchema):
    pass
