from enum import Enum
from typing import List

from pydantic import BaseModel, Field, StrictInt
from typing_extensions import Literal


NODE_OR_EDGE = Literal["Node", "Edge"]
NODE_OR_EDGE_OR_CARRIER = Literal["Node", "Edge", "ElementCarrier"]


class MakeElementEvent(BaseModel):
    element_id: StrictInt = Field(
        ..., description="the id of the element being added to simulation"
    )
    entry_point_kind: NODE_OR_EDGE_OR_CARRIER = Field(
        description="the type of entry point the element is entering at"
    )
    entry_point_id: StrictInt = Field(
        ..., description="the id of the entry point the element is being added at"
    )


class MoveElementsEvent(BaseModel):
    to_move: List[StrictInt] = Field(
        ..., description="the list of IDs of elements to move"
    )
    origin_kind: NODE_OR_EDGE
    origin_id: StrictInt = Field(
        ...,
        description="the id of the original time and location "
        "which the elements are being moved from",
    )
    destination_kind: NODE_OR_EDGE_OR_CARRIER
    destination_id: StrictInt
