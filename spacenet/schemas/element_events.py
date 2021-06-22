from enum import Enum
from typing import List

from pydantic import BaseModel, Field, StrictInt


class EntryPointKind(Enum):
    Node = "Node"
    Edge = "Edge"
    Carrier = "ElementCarrier"


class MoveOriginKind(Enum):
    Node = "Node"
    Edge = "Edge"


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


class MoveElementsEvent(BaseModel):
    to_move: List[StrictInt] = Field(
        ..., description="the list of IDs of elements to move"
    )
    origin_kind: MoveOriginKind
    origin_id: StrictInt = Field(
        ...,
        description="the id of the original time and location "
        "which the elements are being moved from",
    )
    destination_kind: EntryPointKind
    destination_id: StrictInt
