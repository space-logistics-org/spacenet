from enum import Enum

from pydantic import BaseModel, Field, StrictInt


class EntryPointKind(Enum):
    Node = "Node"
    Edge = "Edge"
    Carrier = "ElementCarrier"


class MakeElementEvent(BaseModel):
    element_id: StrictInt = Field(
        ..., description="the id of the element being added to simulation"
    )
    entry_point_kind: EntryPointKind = Field(
        description="the type of entry point the element is entering at"
    )
    entry_point_id: StrictInt = Field(
        ..., description="the id of the entry point the element is being added at"
    )
